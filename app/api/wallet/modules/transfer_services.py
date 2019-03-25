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
#models
from app.api.models import *
# core
from app.api.wallet.modules.transaction_core import TransactionCore
from app.api.wallet.modules.transaction_core import TransactionError
# exceptions
from app.api.error.http import *
#http response
from app.api.http_response import *
# configuration
from app.config import config
# serializer
from app.api.serializer import UserSchema
# utility
from app.api.utility.utils import validate_uuid
# task
from task.transaction.tasks import TransactionTask
from task.bank.tasks import BankTask

WALLET_CONFIG = config.Config.WALLET_CONFIG
TRANSACTION_CONFIG = config.Config.TRANSACTION_CONFIG
TRANSACTION_NOTES = config.Config.TRANSACTION_NOTES
BNI_OPG_CONFIG    = config.Config.BNI_OPG_CONFIG
ERROR_CONFIG = config.Config.ERROR_CONFIG

class TransferServices:
    """ Transfer Services"""

    def __init__(self, source, pin, destination=None):
        source_wallet = Wallet.query.filter_by(id=validate_uuid(source)).first()
        if source_wallet is None:
            raise RequestNotFound(ERROR_CONFIG["WALLET_NOT_FOUND"]["TITLE"],
                                  ERROR_CONFIG["WALLET_NOT_FOUND"]["MESSAGE"])
        #end if

        if source_wallet.is_unlocked() is False:
            raise UnprocessableEntity(ERROR_CONFIG["WALLET_LOCKED"]["TITLE"],
                                      ERROR_CONFIG["WALLET_LOCKED"]["MESSAGE"])
        #end if

        pin_status = source_wallet.check_pin(pin)
        if pin_status == "INCORRECT":
            raise UnprocessableEntity(ERROR_CONFIG["INCORRECT_PIN"]["TITLE"],
                                      ERROR_CONFIG["INCORRECT_PIN"]["MESSAGE"])
        elif pin_status == "MAX_ATTEMPT":
            raise UnprocessableEntity(ERROR_CONFIG["MAX_PIN_ATTEMPT"]["TITLE"],
                                      ERROR_CONFIG["MAX_PIN_ATTEMPT"]["MESSAGE"])
        #end if

        if destination is not None:
            destination_wallet = \
            Wallet.query.filter_by(id=validate_uuid(destination)).first()
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

    def process_instruction(self, params):
        """ process transfer instruction here """
        # if normal transfer
        if params["instructions"] is None:
            self.internal_transfer(params)
        else:
            # loop all instruction
            for instruction in params["instructions"]:
                pass

    @staticmethod
    def calculate_transfer_fee(destination, method=None):
        """ calculate transfer fee based on method and destination"""
        transfer_fee = 0

        bank_account = BankAccount.query.filter_by(id=validate_uuid(destination)).first()
        if bank_account:
            if bank_account.bank.code != "009":
                transfer_fee = WALLET_CONFIG["TRANSFER_FEE"][method]

        return transfer_fee

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
            debit_trx = TransactionCore.debit_transaction(self.source,
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
            credit_trx = TransactionCore.credit_transaction(self.destination,
                                                            credit_payment_id, amount,
                                                            "RECEIVE_TRANSFER",
                                                            transfer_notes)
        except TransactionError as error:
            print(error)
            db.session.rollback()
            raise UnprocessableEntity(ERROR_CONFIG["TRANSFER_FAILED"]["TITLE"],
                                      ERROR_CONFIG["TRANSFER_FAILED"]["MESSAGE"])
        #end if
        return accepted({"id" : str(debit_trx.id)})
    #end def

    def external_transfer(self, params):
        """ method to transfer money externally"""
        bank_account_id = params["destination"]
        amount = params["amount"]
        transfer_notes = params["notes"]

        # calculate transfer fee here
        # for now only online
        transfer_fee = self.calculate_transfer_fee(bank_account_id, "ONLINE")

        if float(amount) + float(transfer_fee) > float(self.source.balance):
            raise UnprocessableEntity(ERROR_CONFIG["INSUFFICIENT_BALANCE"]["TITLE"],
                                      ERROR_CONFIG["INSUFFICIENT_BALANCE"]["MESSAGE"])
        #end if

        # fetch bank information from bank account id here
        bank_account = BankAccount.query.filter_by(id=validate_uuid(bank_account_id)).first()
        if bank_account is None:
            raise RequestNotFound(ERROR_CONFIG["BANK_ACC_NOT_FOUND"]["TITLE"],
                                  ERROR_CONFIG["BANK_ACC_NOT_FOUND"]["MESSAGE"])
        #end if

        # create debit payment
        payment = {
            "payment_type"   : False,
            "source_account" : self.source.id,
            "to"             : bank_account.account_no,
            "amount"         : -amount
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

        # create fee payment if transfer fee > 0
        fee_payment_id = None
        if transfer_fee > 0:
            payment = {
                "payment_type"   : False,
                "source_account" : self.source.id,
                "to"             : "N/A",
                "amount"         : -transfer_fee
            }
            fee_payment_id = self.create_payment(payment)
            try:
                db.session.commit()
            except TransactionError as error:
                print(error)
                db.session.rollback()
                # still commit the master transaction
                raise UnprocessableEntity(ERROR_CONFIG["TRANSFER_FAILED"]["TITLE"],
                                          ERROR_CONFIG["TRANSFER_FAILED"]["MESSAGE"])

        # send queue here
        result = BankTask().bank_transfer.delay(debit_payment_id,
                                                fee_payment_id,
                                                transfer_notes)
        return accepted({"id": str(debit_payment_id)})
    #end def

    @staticmethod
    def checkout(phone_ext, phone_number):
        """
            Checkout Transfer
            exchange phone number and return wallet available for that users
        """
        user = User.query.filter_by(phone_ext=phone_ext,
                                    phone_number=phone_number).first()
        if user is None:
            raise RequestNotFound(ERROR_CONFIG["USER_NOT_FOUND"]["TITLE"],
                                  ERROR_CONFIG["USER_NOT_FOUND"]["MESSAGE"])
        #end if

        # serialize
        user_info = UserSchema(only=('name', 'msisdn','wallets.id',
                                     'wallets.status')).dump(user).data
        return ok(user_info)
    #end def
#end class
