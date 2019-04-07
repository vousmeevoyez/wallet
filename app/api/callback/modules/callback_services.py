"""
    Callback Services
    _________________
    This is module to process business logic from routes and return API
    response
"""
# database
from app.api import db
# model
from app.api.models import *
# services
from app.api.wallets.modules.transfer_services import TransferServices
from app.api.wallets.modules.transaction_core import TransactionCore
# exceptions
from app.api.error.http import *
# configuration
from app.config import config

ERROR_CONFIG = config.Config.ERROR_CONFIG
LOGGING_CONFIG = config.Config.LOGGING_CONFIG

class CallbackServices:
    """ Callback Services Class """

    def __init__(self, virtual_account, trx_id):
        virtual_account = VirtualAccount.query.filter_by(account_no=virtual_account,
                                                         trx_id=trx_id).first()
        if virtual_account is None:
            raise RequestNotFound(ERROR_CONFIG["VA_NOT_FOUND"]["TITLE"],
                                  ERROR_CONFIG["VA_NOT_FOUND"]["MESSAGE"])

        self.virtual_account = virtual_account
    #end def

    def process_callback(self, params):
        """" based on incoming callback decide which method to call """
        payment_amount = int(params["payment_amount"])
        if payment_amount > 0:
            response = self.deposit(params)
        else:
            response = self.withdraw(params)
        return response
    #end def

    def deposit(self, params):
        """
            Function to Deposit Money from Callback
            args:
                params -- parameter
        """
        payment_amount = float(params["payment_amount"])
        reference_number = params["payment_ntb"]
        payment_channel_key = params["payment_channel_key"]

        payment_channel = PaymentChannel.query.filter_by(key=payment_channel_key).first()

        credit_trx = TransactionCore().process_transaction(
            source=self.virtual_account.account_no,
            destination=self.virtual_account.wallet,
            amount=payment_amount,
            payment_type=True,
            transfer_types="TOP_UP",
            channel_id=payment_channel.id,
            reference_number=reference_number
        )

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
 

        transfer_notes = "Cardless Withdraw {}".format(str(-payment_amount))
        debit_trx = TransactionCore().process_transaction(
            source=self.virtual_account.wallet,
            destination=self.virtual_account.account_no,
            amount=-payment_amount,
            payment_type=False,
            transfer_types="WITHDRAW",
            transfer_notes=transfer_notes,
            channel_id=payment_channel.id,
            reference_number=reference_number
        )
        
        response = {
            "status" : "000"
        }
        return response
    #end def
#end class
