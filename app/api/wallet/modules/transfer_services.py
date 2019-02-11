"""
    Transfer Services
    _________________
    this is module that serve request from wallet transfer :w
    routes
"""
#pylint: disable=no-self-use
#pylint: disable=import-error
#pylint: disable=bad-whitespace
#pylint: disable=invalid-name
from sqlalchemy.exc import IntegrityError

from app.api import db
#helper
from app.api.bank.handler import BankHandler
from app.api.common.helper import QR
#models
from app.api.models import *
# exceptions
from app.api.exception.wallet import *

from app.api.exception.bank import BankAccountNotFoundError

from app.api.exception.common import DecryptError
#ttp errors
from app.api.http_response import accepted
from app.api.http_response import no_content
# configuration
from app.config import config

TRANSACTION_CONFIG = config.Config.TRANSACTION_CONFIG
TRANSACTION_NOTES = config.Config.TRANSACTION_NOTES
BNI_OPG_CONFIG    = config.Config.BNI_OPG_CONFIG

class TransferServices:
    """ Transfer Services"""

    def __init__(self, source, pin, destination=None):
        source_wallet = Wallet.query.filter_by(id=source).with_for_update().first()
        if source_wallet is None:
            raise WalletNotFoundError("Source")
        #end if

        if source_wallet.is_unlocked() is False:
            raise WalletLockedError("Source")
        #end if

        if source_wallet.check_pin(pin) is not True:
            raise IncorrectPinError
        #end if

        if destination is not None:
            destination_wallet = \
            Wallet.query.filter_by(id=destination).with_for_update().first()
            if destination_wallet is None:
                raise WalletNotFoundError("Destination")
            #end if

            if destination_wallet.is_unlocked() is False:
                raise WalletLockedError("Destination")
            #end if

            if destination_wallet == source_wallet:
                raise InvalidDestinationError
            #end if

            # set attributes here
            self.destination = destination_wallet
        #end if

        self.source = source_wallet

    @staticmethod
    def create_payment(params):
        """
            Function to create payment
            args:
                params --
                session -- optional
        """
        # build payment object
        payment = Payment(**params)
        try:
            db.session.add(payment)
            db.session.commit()
        except IntegrityError as error:
            db.session.rollback()
            #raise CreatePaymentError
        return payment.id
    #end def

    def internal_transfer(self, params):
        """ method to transfer money internally"""
        amount = params["amount"]
        transfer_notes = params["notes"]

        if float(amount) > float(self.source.balance):
            raise InsufficientBalanceError(self.source.balance, amount)
        #end if

        # create master transaction here that track every transaction
        master_transaction = MasterTransaction(
            source=self.source.id,
            destination=self.destination.id,
            amount=amount
        )
        try:
            db.session.add(master_transaction)
        except IntegrityError:
            db.session.rollback()
        #end def

        # create debit payment
        payment = {
            "payment_type"  : False,# debit
            "source_account": self.source.id,# debit
            "to"            : self.destination.id,# debit
            "amount"        : -amount,# debit
        }

        debit_payment_id = self.create_payment(payment)

        # debit transaction
        try:
            debit_trx = self._debit_transaction(self.source,
                                                debit_payment_id, amount,
                                                "TRANSFER_IN", transfer_notes)
        except TransactionError as error:
            db.session.rollback()
            # still commit the master transaction
            raise TransferError(error)
        #end if

        # append transaction id
        master_transaction.debit_transaction_id = debit_trx.id

        payment = {
            "payment_type"  : True,# credit
            "source_account": self.source.id,# debit
            "to"            : self.destination.id,# debit
            "amount"        : amount,# debit
        }

        credit_payment_id = self.create_payment(payment)
        # credit transaction
        try:
            credit_trx = self.credit_transaction(self.destination,
                                                 credit_payment_id, amount,
                                                 "RECEIVE_TRANSFER",
                                                 transfer_notes)
        except TransactionError as error:
            db.session.rollback()
            raise TransferError(error)
        #end if

        master_transaction.credit_transaction_id = credit_trx.id

        db.session.commit()
        return accepted()
    #end def

    def external_transfer(self, params):
        """ method to transfer money externally"""
        bank_account_id = params["destination"]
        amount = params["amount"]
        transfer_notes = params["notes"]

        if float(amount) > float(self.source.balance):
            raise InsufficientBalanceError(self.source.balance, amount)
        #end if

        # fetch bank information from bank account id here
        bank_account = BankAccount.query.filter_by(id=bank_account_id).first()
        if bank_account is None:
            raise BankAccountNotFoundError

        # create master transaction here that track every transaction
        master_transaction = MasterTransaction(
            source=self.source.id,
            destination=bank_account_id,
            amount=amount
        )
        try:
            db.session.add(master_transaction)
        except IntegrityError as error:
            db.session.rollback()
            raise TransferError(error)
        #end def

        # create debit payment
        payment = {
            "payment_type"   : False,
            "source_account" : self.source.id,
            "to"             : bank_account.account_no,
            "amount"         : amount
        }

        debit_payment_id = self.create_payment(payment)
        # debit transaction
        try:
            debit_trx = self._debit_transaction(self.source,
                                                debit_payment_id, amount,
                                                "TRANSFER_OUT", transfer_notes)
        except TransactionError as error:
            db.session.rollback()
            # still commit the master transaction
            raise TransferError(error)
        #end if

        # append transaction id
        master_transaction.debit_transaction_id = debit_trx.id

        master_transaction.credit_transaction_id = None

        # get information needed for transfer
        payment_payload = {
            "amount"         : amount,
            "source_account" : BNI_OPG_CONFIG["MASTER_ACCOUNT"],
            "account_no"     : bank_account.account_no,
            "bank_code"      : bank_account.bank.code,
        }
        db.session.commit()
        return accepted()
    #end def

    @staticmethod
    def _debit_transaction(wallet, payment_id, amount, flag,
                           transfer_notes=None):
        amount = -float(amount)

        # fetch transaction type from config
        transaction_type = TRANSACTION_CONFIG["TYPES"][flag]

        # deduct balance first
        wallet.add_balance(amount)

        if transfer_notes is None:
            notes = TRANSACTION_NOTES["SEND_TRANSFER"].format(str(-amount))
        else:
            notes = transfer_notes
        #end if

        # debit (-) we increase balance
        debit_transaction = Transaction(
            payment_id=payment_id,
            wallet_id=wallet.id,
            amount=amount,
            transaction_type=transaction_type,
            notes=notes
        )
        debit_transaction.generate_trx_id()

        try:
            db.session.add(debit_transaction)
            db.session.commit()
        except IntegrityError as error:
            db.session.rollback()
            raise TransactionError(error)
        #end try
        return debit_transaction
    #end def

    @staticmethod
    def credit_transaction(wallet, payment_id, amount, flag,
                           transfer_notes=None):
        """ create credit transaction and add balance """
        transaction_type = TRANSACTION_CONFIG["TYPES"][flag]

        if transfer_notes is None:
            notes = TRANSACTION_NOTES["RECEIVE_TRANSFER"].format(str(amount))
        else:
            notes = transfer_notes
        #end if

        # credit (+) we increase balance
        credit_transaction = Transaction(
            payment_id=payment_id,
            wallet_id=wallet.id,
            amount=amount,
            transaction_type=transaction_type,
            notes=notes
        )
        credit_transaction.generate_trx_id()

        wallet.add_balance(amount)
        try:
            db.session.add(credit_transaction)
            db.session.commit()
        except IntegrityError as error:
            db.session.rollback()
            raise TransactionError(error)
        #end try
        return credit_transaction
    #end def
#end class
