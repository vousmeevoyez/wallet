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
from sqlalchemy.exc import IntegrityError, InvalidRequestError

from app.api import db
#helper
from app.api.bank.handler import BankHandler
from app.api.common.helper import QR
#models
from app.api.models import Wallet
from app.api.models import Transaction
from app.api.models import Payment
from app.api.models import BankAccount
from app.api.models import MasterTransaction
# exceptions
from app.api.exception.wallet import WalletNotFoundError
from app.api.exception.wallet import WalletLockedError
from app.api.exception.wallet import IncorrectPinError
from app.api.exception.wallet import InsufficientBalanceError
from app.api.exception.wallet import InvalidDestinationError
from app.api.exception.wallet import TransactionError
from app.api.exception.wallet import TransferError

from app.api.exception.common import DecryptError
#ttp errors
from app.api.http_response import accepted
from app.api.http_response import no_content
# configuration
from app.config import config

WALLET_CONFIG     = config.Config.WALLET_CONFIG
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
        #end if

        if destination_wallet == source_wallet:
            raise InvalidDestinationError
        #end if

        self.source = source_wallet
        self.destination = destination_wallet


    @staticmethod
    def _create_payment(params):
        """
            Function to create payment
            args:
                params --
                session -- optional
        """
        source_account = params["source"]
        to             = params["destination"]
        amount         = params["amount"]
        payment_type   = params["payment_type"]

        # build payment object
        payment = Payment(
            source_account=source_account,
            to=to,
            amount=amount,
            payment_type=payment_type,
        )
        try:
            db.session.add(payment)
            db.session.commit()
        except IntegrityError as error:
            db.session.rollback()
            #raise CreatePaymentError
        return payment.id
    #end def

    def qr_transfer(self, params):
        """
            Function to transfer between wallet using qr code
            args:
                params --
        """
        try:
            encrypted_payload = QR().read(params["qr_string"])
        except DecryptError:
            # raises
            pass
        #end try
        params["destination"] = encrypted_payload["wallet_id"]
        return self.internal_transfer(params)
    #end def

    def internal_transfer(self, params):
        """ method to transfer money internally"""
        amount = params["amount"]

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
        params["payment_type"] = False # debit
        params["source"] = self.source.id
        params["destination"] = self.destination.id

        debit_payment_id = self._create_payment(params)

        # debit transaction
        try:
            debit_trx = self._debit_transaction(self.source,
                                                debit_payment_id, amount, "IN")
        except TransactionError as error:
            db.session.rollback()
            # still commit the master transaction
            raise TransferError(error)
        #end if

        # append transaction id
        master_transaction.debit_transaction_id = debit_trx.id

        # create credit payment
        params["payment_type"] = True # credit
        params["source"] = self.source.id
        params["destination"] = self.destination.id

        credit_payment_id = self._create_payment(params)
        # credit transaction
        try:
            credit_trx = self._credit_transaction(self.destination,
                                                  credit_payment_id, amount)
        except TransactionError as error:
            db.session.rollback()
            raise TransferError(error)
        #end if

        master_transaction.credit_transaction_id = credit_trx.id

        db.session.commit()
        return accepted()
    #end def

    def external_transfer(self, params):
        bank_account_id = params["destination"]
        amount          = params["amount"]

        if float(amount) > float(self.source.balance):
            raise InsufficientBalanceError(self.source.balance, amount)
        #end if

        # fetch bank information from bank account id here
        bank_account = BankAccount.query.filter_by(id=bank_account_id).first()

        # get information needed for transfer
        payment_payload = {
            "amount"         : amount,
            "source_account" : BNI_OPG_CONFIG["MASTER_ACCOUNT"],
            "account_no"     : bank_account.account_no,
            "bank_code"      : bank_account.bank.code,
        }
        payment_response = BankHandler("BNI").dispatch("DIRECT_TRANSFER",
                                                       payment_payload)
        if payment_response["status"] != "SUCCESS":
            response["status"] = "SERVER_ERROR"
            response["data"] = RESPONSE_MSG["FAILED"]["TRANSFER_FAILED"]
            return response
        #end if

        # create debit payment
        params["payment_type"] = False # debit
        debit_payment_id = self._create_payment(params, session)

        # debit transaction
        try:
            self._debit_transaction(source_wallet, debit_payment_id, amount,\
                                    "OUT", session)
        except TransactionError as error:
            raise TransferError(error)
        #end if

        session.commit()
        return response
    #end def

    @staticmethod
    def _debit_transaction(wallet, payment_id, amount, flag):
        amount = -float(amount)

        if flag == "IN":
            transaction_type = WALLET_CONFIG["IN_TRANSFER"]
        else:
            transaction_type = WALLET_CONFIG["OUT_TRANSFER"]
        #end if

        # deduct balance first
        wallet.add_balance(amount)

        # debit (-) we increase balance
        debit_transaction = Transaction(
            payment_id=payment_id,
            wallet_id=wallet.id,
            amount=amount,
            transaction_type=transaction_type,
            notes=TRANSACTION_NOTES["SEND_TRANSFER"].format(str(amount))
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
    def _credit_transaction(wallet, payment_id, amount):
        amount = float(amount)
        # credit (+) we increase balance
        credit_transaction = Transaction(
            payment_id=payment_id,
            wallet_id=wallet.id,
            amount=amount,
            transaction_type=WALLET_CONFIG["IN_TRANSFER"],
            notes=TRANSACTION_NOTES["RECEIVE_TRANSFER"].format(str(amount))
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
