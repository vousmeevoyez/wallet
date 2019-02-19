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
from app.api.common.helper import QR
#models
from app.api.models import *
# exceptions
from app.api.error.http import *
#ttp errors
from app.api.http_response import accepted
from app.api.http_response import no_content
# configuration
from app.config import config
# task
from task.bank.tasks import TransactionTask

TRANSACTION_LOG_CONFIG = config.Config.TRANSACTION_LOG_CONFIG
TRANSACTION_CONFIG = config.Config.TRANSACTION_CONFIG
TRANSACTION_NOTES = config.Config.TRANSACTION_NOTES
BNI_OPG_CONFIG    = config.Config.BNI_OPG_CONFIG
ERROR_CONFIG = config.Config.ERROR_CONFIG

class TransactionError(Exception):
    """ raised when something occured on creating transaction """
    def __init__(self, original_exception):
        super().__init__(original_exception)
        self.original_exception = original_exception

class TransferServices:
    """ Transfer Services"""

    def __init__(self, source, pin, destination=None):
        source_wallet = Wallet.query.filter_by(id=source).with_for_update().first()
        if source_wallet is None:
            raise RequestNotFound(ERROR_CONFIG["WALLET_NOT_FOUND"]["TITLE"],
                                  ERROR_CONFIG["WALLET_NOT_FOUND"]["MESSAGE"])
        #end if

        if source_wallet.is_unlocked() is False:
            raise UnprocessableEntity(ERROR_CONFIG["WALLET_LOCKED"]["TITLE"],
                                      ERROR_CONFIG["WALLET_LOCKED"]["MESSAGE"])
        #end if

        if source_wallet.check_pin(pin) is not True:
            raise UnprocessableEntity(ERROR_CONFIG["INCORRECT_PIN"]["TITLE"],
                                      ERROR_CONFIG["INCORRECT_PIN"]["MESSAGE"])
        #end if

        if destination is not None:
            destination_wallet = \
            Wallet.query.filter_by(id=destination).with_for_update().first()
            if destination_wallet is None:
                raise RequestNotFound(ERROR_CONFIG["WALLET_NOT_FOUND"]["TITLE"],
                                      ERROR_CONFIG["WALLET_NOT_FOUND"]["MESSAGE"])
            #end if

            if destination_wallet.is_unlocked() is False:
                raise UnprocessableEntity(ERROR_CONFIG["WALLET_LOCKED"]["TITLE"],
                                          ERROR_CONFIG["WALLET_LOCKED"]["MESSAGE"])
            #end if

            if destination_wallet == source_wallet:
                raise UnprocessableEntity(ERROR_CONFIG["INVALID_DESTINATION"]["TITLE"],
                                          ERROR_CONFIG["INVALID_DESTINATION"]["MESSAGE"])
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
            raise UnprocessableEntity(ERROR_CONFIG["INSUFFICIENT_BALANCE"]["TITLE"],
                                      ERROR_CONFIG["INSUFFICIENT_BALANCE"]["MESSAGE"])
        #end if

        # create debit payment
        payment = {
            "payment_type"  : False,# debit
            "source_account": self.source.id,# debit
            "to"            : self.destination.id,# debit
            "amount"        : -amount,# debit
        }

        debit_payment_id = self.create_payment(payment)
        try:
            db.session.commit()
        except TransactionError as error:
            print(error)
            db.session.rollback()
            # still commit the master transaction
            raise UnprocessableEntity(ERROR_CONFIG["TRANSFER_FAILED"]["TITLE"],
                                      ERROR_CONFIG["TRANSFER_FAILED"]["MESSAGE"])

        # debit transaction
        try:
            debit_trx = self.debit_transaction(self.source,
                                               debit_payment_id, amount,
                                               "TRANSFER_IN", transfer_notes)
        except TransactionError as error:
            print(error)
            db.session.rollback()
            # still commit the master transaction
            raise UnprocessableEntity(ERROR_CONFIG["TRANSFER_FAILED"]["TITLE"],
                                      ERROR_CONFIG["TRANSFER_FAILED"]["MESSAGE"])
        #end if

        payment = {
            "payment_type"  : True,# credit
            "source_account": self.source.id,# debit
            "to"            : self.destination.id,# debit
            "amount"        : amount,# debit
        }

        credit_payment_id = self.create_payment(payment)
        try:
            db.session.commit()
        except IntegrityError as error:
            print(error)
            db.session.rollback()
            raise UnprocessableEntity(ERROR_CONFIG["TRANSFER_FAILED"]["TITLE"],
                                      ERROR_CONFIG["TRANSFER_FAILED"]["MESSAGE"])
        #end try

        # credit transaction
        try:
            credit_trx = self.credit_transaction(self.destination,
                                                 credit_payment_id, amount,
                                                 "RECEIVE_TRANSFER",
                                                 transfer_notes)
        except TransactionError as error:
            print(error)
            db.session.rollback()
            raise UnprocessableEntity(ERROR_CONFIG["TRANSFER_FAILED"]["TITLE"],
                                      ERROR_CONFIG["TRANSFER_FAILED"]["MESSAGE"])
        #end if
        return accepted()
    #end def

    def external_transfer(self, params):
        """ method to transfer money externally"""
        bank_account_id = params["destination"]
        amount = params["amount"]
        transfer_notes = params["notes"]

        if float(amount) > float(self.source.balance):
            raise UnprocessableEntity(ERROR_CONFIG["INSUFFICIENT_BALANCE"]["TITLE"],
                                      ERROR_CONFIG["INSUFFICIENT_BALANCE"]["MESSAGE"])
        #end if

        # fetch bank information from bank account id here
        bank_account = BankAccount.query.filter_by(id=bank_account_id).first()
        if bank_account is None:
            raise RequestNotFound(ERROR_CONFIG["BANK_ACC_NOT_FOUND"]["TITLE"],
                                  ERROR_CONFIG["BANK_ACC_NOT_FOUND"]["MESSAGE"])

        # create debit payment
        payment = {
            "payment_type"   : False,
            "source_account" : self.source.id,
            "to"             : bank_account.account_no,
            "amount"         : amount
        }

        debit_payment_id = self.create_payment(payment)
        try:
            db.session.commit()
        except TransactionError as error:
            print(error)
            db.session.rollback()
            # still commit the master transaction
            raise UnprocessableEntity(ERROR_CONFIG["TRANSFER_FAILED"]["TITLE"],
                                      ERROR_CONFIG["TRANSFER_FAILED"]["MESSAGE"])

        # debit transaction
        try:
            debit_trx = self.debit_transaction(self.source,
                                                debit_payment_id, amount,
                                                "TRANSFER_OUT", transfer_notes)
        except TransactionError as error:
            print(error)
            db.session.rollback()
            # still commit the master transaction
            raise UnprocessableEntity(ERROR_CONFIG["TRANSFER_FAILED"]["TITLE"],
                                      ERROR_CONFIG["TRANSFER_FAILED"]["MESSAGE"])
        #end if
        # send queue here
        return accepted()
    #end def

    @staticmethod
    def debit_transaction(wallet, payment_id, amount, flag,
                          transfer_notes=None):

        amount = -amount

        # fetch transaction type from config
        transaction_type = TRANSACTION_CONFIG["TYPES"][flag]

        if transfer_notes is None:
            notes = TRANSACTION_NOTES["SEND_TRANSFER"].format(str(amount))
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
        except IntegrityError as error:
            db.session.rollback()
            raise TransactionError(error)
        #end try
        # should send queue here
        result = TransactionTask().transfer.delay(payment_id)
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
        try:
            db.session.add(credit_transaction)
            db.session.commit()
        except IntegrityError as error:
            db.session.rollback()
            raise TransactionError(error)
        #end try
        # send queue here
        result = TransactionTask().transfer.delay(payment_id)
        return credit_transaction
    #end def
#end class
