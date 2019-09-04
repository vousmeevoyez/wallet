"""
    Wallet Routes
    _______________
"""
#pylint: disable=import-error
#pylint: disable=invalid-name
#pylint: disable=no-self-use
#pylint: disable=too-few-public-methods
#pylint: disable=no-name-in-module

from app.api.core import Routes

from app.api.wallets import api
#serializer
from app.api.serializer import *
# request schema
from app.api.request_schema import *
# wallet modules
from app.api.wallets.modules.wallet_services import WalletServices
from app.api.wallets.modules.withdraw_services import WithdrawServices
from app.api.transfer.modules.transfer_services import TransferServices
# transaction modules
from app.api.transactions.modules.transaction_services import TransactionServices
# authentication
from app.api.auth.decorator import token_required
from app.api.auth.decorator import get_token_payload
from app.api.auth.decorator import api_key_required
# utility
from app.api.utility.utils import QR

# exceptions
from app.api.utility.utils import UtilityError
from app.api.error.http import BadRequest

# configuration
from app.config import config

@api.route('/')
class WalletAddRoutes(Routes):
    """
        Wallets
        /wallets/
    """
    __schema__ = WalletRequestSchema
    __serializer__ = WalletSchema(strict=True)

    @token_required
    def post(self):
        """ endpoint for creating wallet """
        token_payload = get_token_payload()
        user = token_payload["user"]

        request_data = self.payload()
        wallet = self.serialize(request_data, load=True)

        response = WalletServices().add(user, wallet, request_data["pin"])
        return response
    #end def

    @token_required
    def get(self):
        """ endpoint for getting wallet information """
        payload = get_token_payload()
        user = payload["user"]

        response = WalletServices.show(user)
        return response
    #end def
#end class

@api.route('/<string:wallet_id>')
class WalletRoutes(Routes):
    """
        Wallet Routes
        api/v1/wallet/
    """
    @token_required
    def get(self, wallet_id):
        """ endpoint for getting wallet information """
        response = WalletServices(wallet_id).info()
        return response
    #end def

    def delete(self, wallet_id):
        """ endpoint for removing wallet """
        response = WalletServices(wallet_id).remove()
        return response
    #end def
#end class

@api.route('/<string:wallet_id>/qr/')
class WalletQrRoutes(Routes):
    """
        Wallet QR
        /<wallet_id>/qr
    """
    @token_required
    def get(self, wallet_id):
        """ endpoint for getting wallet qr codes """
        response = WalletServices(wallet_id).get_qr()
        return response
    #end def
#end class

@api.route('/<string:wallet_id>/qr/checkout')
class WalletQrTransferRoutes(Routes):
    """
        Wallet QR Checkout
        /<wallet_id>/qr/checkout
    """
    __schema__ = QRTransferRequestSchema

    def preprocess(self, payload):
        # Decrypt QR Code here
        try:
            payload = QR().read(payload["qr_string"])
        except UtilityError:
            raise BadRequest(self.error_response["INVALID_QR"]["TITLE"],
                             self.error_response["INVALID_QR"]["MESSAGE"])
        #end try
        return payload
    # end def

    @token_required
    def post(self, wallet_id):
        """ endpoint for checking out qr """
        # request data validator
        request_data = self.serialize(self.payload())

        response = WalletServices(request_data["wallet_id"]).owner_info()
        return response
    #end def
#end class

@api.route('/<string:wallet_id>/balance/')
class WalletBalanceRoutes(Routes):
    """
        Wallet Balance
        /<wallet_id>/balance
    """
    @token_required
    def get(self, wallet_id):
        """ endpoint for getting wallet balance """
        response = WalletServices(wallet_id).check_balance()
        return response
    #end def
#end class

@api.route('/<string:wallet_id>/transactions')
class WalletTransactionRoutes(Routes):
    """
        Wallet Transaction
        /<wallet_id>/transactions
    """

    __schema__ = WalletTransactionRequestSchema
    __serializer__ = WalletTransactionSchema(strict=True)

    @token_required
    def get(self, wallet_id):
        """ endpoint for getting wallet transaction """
        request_data = self.serialize(self.payload())

        response = TransactionServices(wallet_id).history(request_data)
        return response
    #end def
#end class

@api.route('/<string:wallet_id>/transactions/<transaction_id>')
class WalletTransactionDetailsRoutes(Routes):
    """
        Wallet Transaction Details
        /<wallet_id>/transactions/<transaction_id>
    """
    @token_required
    def get(self, wallet_id, transaction_id):
        """ endpoint for getting transaction details """
        response = TransactionServices(wallet_id, transaction_id).history_details()
        return response
    #end def
#end class

@api.route('/<string:wallet_id>/pin/')
class WalletPinRoutes(Routes):
    """
        Wallet pin
        /<wallet_id>/pin/
    """

    __schema__ = WalletUpdatePinRequestSchema
    __serializer__ = UpdatePinSchema(strict=True)

    @token_required
    def put(self, wallet_id):
        """ endpoint for updating wallet pin """
        request_data = self.serialize(self.payload())
        response = WalletServices(wallet_id).update_pin(request_data)
        return response
    #end def

    @token_required
    def post(self, wallet_id):
        """ endpoint for checking pin """
        self.__schema__ = PinOnlyRequestSchema
        self.__serializer__ = TransactionSchema(only=("pin"))

        request_data = self.serialize(self.payload())
        response = WalletServices(wallet_id, request_data["pin"]).check()
        return response
    #end def
#end class

@api.route('/<string:wallet_id>/forgot/')
class WalletForgotPinRoutes(Routes):
    """
        Wallet Forgot Pin
        /<wallet_id>/forgot/
    """

    __schema__ = ForgotPinRequestSchema

    @token_required
    def get(self, wallet_id):
        """ forgot pin request """
        response = WalletServices(wallet_id).send_forgot_otp()
        return response
    #end def

    @token_required
    def post(self, wallet_id):
        """ verify forgot pin """
        request_data = self.payload()

        response = WalletServices(wallet_id).verify_forgot_otp(request_data)
        return response
    #end def
#end class

@api.route('/<string:wallet_id>/withdraw/')
class WalletWithdrawRoutes(Routes):
    """
        Wallet Withdraw
        /<wallet_id>/withdraw/
    """

    __schema__ = WithdrawRequestSchema
    __serializer__ = TransactionSchema(strict=True, only=("pin", "amount"))

    @token_required
    def post(self, wallet_id):
        """ endpoint for withdraw request """
        request_data = self.serialize(self.payload())

        request_data["bank_name"] = "BNI"
        response = WithdrawServices(wallet_id,
                                    request_data["pin"]).request(request_data)
        return response
    #end def
#end class

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
