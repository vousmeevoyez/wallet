"""
    Transfer Routes
    _______________
"""
# pylint: disable=import-error
# pylint: disable=invalid-name
# pylint: disable=no-self-use
# pylint: disable=too-few-public-methods
# pylint: disable=no-name-in-module

from app.api.core import Routes

from app.api.transfer import api

# serializer
from app.api.serializer import *

# request schema
from app.api.request_schema import *

# transfer modules
from app.api.transfer.modules.transfer_services import TransferServices

# authentication
from app.api.auth.decorator import token_required, get_token_payload, api_key_required

# utility
from app.api.utility.utils import QR

# exceptions
from app.api.utility.utils import UtilityError
from app.api.error.http import BadRequest

# configuration
from app.config import config


'''
@api.route('/<string:source_wallet_id>/transfer/checkout')
class TransferCheckoutRoutes(Routes):
    """
        Transfer Checkout
        /<source>/transfer/checkout
    """

    __schema__ = TransferCheckoutRequestSchema
    __serializer__ = UserSchema(strict=True, only=("phone_ext", "phone_number"))

    @token_required
    def post(self, source_wallet_id):
        """ endpoint for checking out wallet before transfer """
        # parse request data
        request_data = self.serialize(self.payload())
        response = TransferServices().checkout(
            request_data["phone_ext"], request_data["phone_number"])
        return response
    #end def
#end class

################################## PATCH ############################################
@api.route('/transfer/checkout2')
class TransferCheckout2Routes(Routes):
    """
        Transfer Checkout
        /<source>/transfer/checkout
    """

    __schema__ = TransferCheckoutRequestSchema
    __serializer__ = UserSchema(strict=True, only=("phone_ext", "phone_number"))

    @api_key_required
    def post(self):
        """ endpoint for checking out wallet before transfer """
        request_data = self.serialize(self.payload())
        response = TransferServices().checkout2(
            request_data["phone_ext"], request_data["phone_number"])
        return response
    #end def
#end class

@api.route('/<string:source_wallet_id>/transfer/<string:destination_wallet_id>')
class TransferTransferRoutes(Routes):
    """
        Transfer Transfer
        /<source>/transfer/<destination>
    """

    __schema__ = TransferRequestSchema
    __serializer__ = TransactionSchema(strict=True, only=("pin", "amount"))

    @token_required
    def post(self, source_wallet_id, destination_wallet_id):
        """ endpoint for executing transfer between wallet """
        # parse request data
        request_data = self.serialize(self.payload())

        response = TransferServices(source_wallet_id,
                                    request_data["pin"],
                                    destination_wallet_id).internal_transfer(request_data)
        return response
    #end def
#end class

@api.route('/<string:source_wallet_id>/transfer/bank/<string:bank_account_id>')
class TransferBankTransferRoutes(Routes):
    """
        Transfer Bank Transfer Routes
        /source/transfer/bank/<bank_account_id>
    """

    __schema__ = TransferRequestSchema
    __serializer__ = TransactionSchema(strict=True, only=("pin", "amount"))

    @token_required
    def post(self, source_wallet_id, bank_account_id):
        """ endpoint for executing bank transfer """
        # parse request data
        request_data = self.serialize(self.payload())

        request_data["destination"] = bank_account_id
        response = TransferServices(source_wallet_id,
                                    request_data["pin"]).external_transfer(request_data)
        return response
    #end def
#end class

################################## PATCH ############################################
@api.route('/<string:source_wallet_id>/transfer/bank2/<string:bank_account_id>')
class TransferBankTransfer2Routes(Routes):
    """
        Transfer Bank Transfer Routes
        /source/transfer/bank/<bank_account_id>
    """

    __schema__ = TransferRequestSchema
    __serializer__ = TransactionSchema(strict=True, only=("pin", "amount"))

    @api_key_required
    def post(self, source_wallet_id, bank_account_id):
        """ endpoint for executing bank transfer """
        request_data = self.serialize(self.payload())

        request_data["destination"] = bank_account_id
        response = TransferServices(source_wallet_id,
                                    request_data["pin"]).external_transfer(request_data)
        return response
    #end def
#end class
'''
