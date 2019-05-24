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

class Callback:
    """ Base Callback """
    def __init__(self, virtual_account, trx_id, flow):
        """
            virtual_account -> virtual_account no
            trx_id -> virtual_account trx_id
            flow -> IN | OUT
        """
        virtual_account = VirtualAccount.query.filter_by(account_no=virtual_account,
                                                         trx_id=trx_id).first()
        if virtual_account is None:
            raise RequestNotFound(ERROR_CONFIG["VA_NOT_FOUND"]["TITLE"],
                                  ERROR_CONFIG["VA_NOT_FOUND"]["MESSAGE"])

        self.virtual_account = virtual_account
        self.flow = flow
    #end def

    def process(self, amount, payment_type, transfer_types, reference_number, channel, transfer_notes=None):
        """ base method for processing callback """
        # lookup channel and get his channel id
        payment_channel = PaymentChannel.query.filter_by(key=channel).first()

        # convert flow to source -> destination or destination -> source
        source = "account_no"
        destination = "wallet"
        if self.flow == "OUT":
            source = "wallet"
            destination = "account_no"
        # end if

        trx = TransactionCore().process_transaction(
            source=getattr(self.virtual_account, source),
            destination=getattr(self.virtual_account, destination),
            amount=amount,
            payment_type=payment_type,
            transfer_types=transfer_types,
            channel_id=payment_channel.id,
            transfer_notes=transfer_notes,
            reference_number=reference_number
        )
        # accepted BNI Format
        response = {
            "status" : "000"
        }
        return response
    # end def
# end class

class CallbackServices(Callback):
    """ Callback Services Class """

    def process_callback(self, params):
        """" based on incoming callback decide which method to call """
        payment_amount = int(params["payment_amount"])
        reference_number = params["payment_ntb"]
        payment_channel_key = params["payment_channel_key"]

        if payment_amount > 0:
            response = super().process(payment_amount, True, "TOP_UP", reference_number,
                                       payment_channel_key)
        else:
            transfer_notes = "Cardless Withdraw {}".format(str(-payment_amount))
            response = super().process(abs(payment_amount), False, "WITHDRAW", reference_number,
                                       payment_channel_key, transfer_notes)
        return response
    #end def
#end class
