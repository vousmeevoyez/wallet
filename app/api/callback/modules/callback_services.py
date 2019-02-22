"""
    Callback Services
    _________________
    This is module to process business logic from routes and return API
    response
"""
from sqlalchemy.exc import IntegrityError

from app.api import db
from app.api.models import *

from app.config import config

from app.api.wallet.modules.transfer_services import TransferServices
from app.api.wallet.modules.transfer_services import TransactionError

from app.api.error.http import *

ERROR_CONFIG = config.Config.ERROR_CONFIG
LOGGING_CONFIG = config.Config.LOGGING_CONFIG

class CallbackServices:
    """ Callback Services Class to handle all callback process here"""

    def __init__(self, virtual_account, trx_id):
        virtual_account = VirtualAccount.query.filter_by(account_no=virtual_account,
                                                         trx_id=trx_id).first()
        if virtual_account is None:
            raise RequestNotFound(ERROR_CONFIG["VA_NOT_FOUND"]["TITLE"],
                                  ERROR_CONFIG["VA_NOT_FOUND"]["MESSAGE"])

        self.virtual_account = virtual_account
    #end def

    def deposit(self, params):
        """
            Function to Deposit Money from Callback
            args:
                params -- parameter
        """
        payment_amount = params["payment_amount"]
        reference_number = params["payment_ntb"]
        payment_channel_key = params["payment_channel_key"]

        payment_channel = PaymentChannel.query.filter_by(key=payment_channel_key).first()

        # create log here
        log = Log()
        db.session.add(log)

        # create payment
        payment_payload = {
            "channel_id"    : payment_channel.id,
            "source_account": self.virtual_account.account_no,
            "to"            : self.virtual_account.wallet_id,
            "ref_number"    : reference_number,
            "amount"        : payment_amount,
            "payment_type"  : True # Credit
        }
        payment_id = TransferServices.create_payment(payment_payload)
        log.payment_id = payment_id

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        #end def

        wallet = self.virtual_account.wallet
        amount = payment_amount

        try:
            credit_transaction = TransferServices.credit_transaction(wallet,
                                                                     payment_id,
                                                                     amount,
                                                                     "TOP_UP")
        except TransactionError as error:
            db.session.rollback()
            raise UnprocessableEntity(ERROR_CONFIG["DEPOSIT_CALLBACK_FAILED"]["TITLE"],
                                      ERROR_CONFIG["DEPOSIT_CALLBACK_FAILED"]["MESSAGE"])
        #end def
        response = {
            "status" : "000"
        }
        return response
    #end def

    def withdraw(self, params):
        """
            Function to Withdraw Money from Callback
            args:
                params -- parameter
        """
        payment_amount = abs(float(params["payment_amount"]))
        reference_number = params["payment_ntb"]
        payment_channel_key = params["payment_channel_key"]

        payment_channel = PaymentChannel.query.filter_by(key=payment_channel_key).first()

        # create log here
        log = Log()
        db.session.add(log)

        # create payment
        payment_payload = {
            "channel_id"    : payment_channel.id,
            "source_account": self.virtual_account.wallet_id,
            "to"            : self.virtual_account.account_no,
            "ref_number"    : reference_number,
            "amount"        : -payment_amount,
            "payment_type"  : False #DEBIT
        }
        payment_id = TransferServices.create_payment(payment_payload)
        log.payment_id = payment_id

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        #end def

        wallet = self.virtual_account.wallet

        try:
            transfer_notes = "Cardless Withdraw {}".format(str(-payment_amount))
            debit_transaction = TransferServices.debit_transaction(wallet,
                                                                   payment_id,
                                                                   payment_amount,
                                                                   "WITHDRAW",
                                                                   transfer_notes)
        except TransactionError as error:
            db.session.rollback()
            raise UnprocessableEntity(ERROR_CONFIG["WITHDRAW_CALLBACK_FAILED"]["TITLE"],
                                      ERROR_CONFIG["WITHDRAW_CALLBACK_FAILED"]["MESSAGE"])
        #end def
        response = {
            "status" : "000"
        }
        return response
    #end def
#end class
