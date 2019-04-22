"""
    Wallet Routes
    _______________
    this is module that handle rquest from url and then forward it to services
"""
#pylint: disable=import-error
#pylint: disable=invalid-name
#pylint: disable=no-self-use
#pylint: disable=too-few-public-methods

from flask_restplus import Resource
from marshmallow import ValidationError

from app.api.wallets import api
#serializer
from app.api.serializer import *
# request schema
from app.api.request_schema import *
# wallet modules
from app.api.wallets.modules.wallet_services import WalletServices
from app.api.wallets.modules.transfer_services import TransferServices
from app.api.wallets.modules.withdraw_services import WithdrawServices
# transaction modules
from app.api.transactions.modules.transaction_services import TransactionServices
# authentication
from app.api.auth.decorator import token_required
from app.api.auth.decorator import get_token_payload
from app.api.auth.decorator import admin_required
from app.api.auth.decorator import api_key_required
# utility
from app.api.utility.utils import QR
from app.api.utility.modules.cipher import DecryptError
# exceptions
from app.api.error.http import *
# configuration
from app.config import config

class BaseRoutes(Resource):
    error_response = config.Config.ERROR_CONFIG

@api.route('/')
class WalletAddRoutes(BaseRoutes):
    """
        Wallet add Routes
        api/v1/wallet/<user_id>
    """
    @token_required
    def post(self):
        """
            Handle POST request from
            api/v1/wallet/<user_id>
        """
        payload = get_token_payload()
        user = payload["user"]

        request_data = WalletRequestSchema.parser.parse_args(strict=True)
        try:
            wallet = WalletSchema(strict=True).load(request_data)
        except ValidationError as error:
            raise BadRequest(self.error_response["INVALID_PARAMETER"]["TITLE"],
                             self.error_response["INVALID_PARAMETER"]["MESSAGE"],
                             error.messages)

        response = WalletServices().add(user, wallet.data, request_data["pin"])
        return response
    #end def

    @token_required
    def get(self):
        """
            Handle GET request from
            api/v1/wallet/<user_id>
        """
        payload = get_token_payload()
        user = payload["user"]

        response = WalletServices.show(user)
        return response
    #end def
#end class

@api.route('/<string:wallet_id>')
class WalletRoutes(BaseRoutes):
    """
        Wallet Routes
        api/v1/wallet/
    """
    @token_required
    def get(self, wallet_id):
        """
            handle GET method from
            api/v1/wallet/
            return wallet information
        """
        response = WalletServices(wallet_id).info()
        return response
    #end def

    def delete(self, wallet_id):
        """
            handle DELETE method from
            api/v1/wallet/
        """
        response = WalletServices(wallet_id).remove()
        return response
    #end def
#end class

@api.route('/<string:wallet_id>/qr/')
class WalletQrRoutes(BaseRoutes):
    """
        Wallet QR Routes
        api/v1/<wallet_id>/qr
    """
    @token_required
    def get(self, wallet_id):
        """
            handle GET method from
            api/v1/<wallet_id>/qr
            return wallet qr
        """
        response = WalletServices(wallet_id).get_qr()
        return response
    #end def
#end class

@api.route('/<string:wallet_id>/qr/checkout')
class WalletQrTransferRoutes(BaseRoutes):
    """
        Wallet QR Routes
        api/v1/<wallet_id>/qr
    """
    @token_required
    def post(self, wallet_id):
        """
            handle GET method from
            api/v1/<wallet_id>/qr
            return wallet qr
        """
        # request data validator
        request_data = QRTransferRequestSchema.parser.parse_args(strict=True)
        # Decrypt QR Code here
        try:
            payload = QR().read(request_data["qr_string"])
        except DecryptError:
            raise BadRequest(self.error_response["INVALID_QR"]["TITLE"],
                             self.error_response["INVALID_QR"]["MESSAGE"])
        #end try
        response = WalletServices(payload["wallet_id"]).owner_info()
        return response
    #end def
#end class

@api.route('/<string:wallet_id>/balance/')
class WalletBalanceRoutes(BaseRoutes):
    """
        Wallet Balance Routes
        api/v1/<wallet_id>/balance
    """
    @token_required
    def get(self, wallet_id):
        """
            handle GET method from
            api/v1/<wallet_id>/balance
            return wallet balance
        """
        response = WalletServices(wallet_id).check_balance()
        return response
    #end def
#end class

@api.route('/<string:wallet_id>/transactions')
class WalletTransactionRoutes(BaseRoutes):
    """
        Wallet Transaction Routes
        api/v1/<wallet_id>/transactions
    """
    @token_required
    def get(self, wallet_id):
        """
            handle GET method from
            api/v1/<wallet_id>/transactions
            return wallet transaction list
        """
        request_data = WalletTransactionRequestSchema.parser.parse_args(strict=True)
        try:
            wallet = WalletTransactionSchema(strict=True).validate(request_data)
        except ValidationError as error:
            raise BadRequest(self.error_response["INVALID_PARAMETER"]["TITLE"],
                             self.error_response["INVALID_PARAMETER"]["MESSAGE"],
                             error.messages)

        response = TransactionServices(wallet_id).history(request_data)
        return response
    #end def
#end class

@api.route('/<string:wallet_id>/transactions/<transaction_id>')
class WalletTransactionDetailsRoutes(BaseRoutes):
    """
        Wallet Transaction Details Routes
        api/v1/<wallet_id>/transactions/<transaction_id>
    """
    @token_required
    def get(self, wallet_id, transaction_id):
        """
            handle GET method from
            api/v1/<wallet_id>/transactions/<transaction_id>
            return wallet transaction details
        """
        response = TransactionServices(wallet_id, transaction_id).history_details()
        return response
    #end def
#end class

@api.route('/<string:wallet_id>/pin/')
class WalletPinRoutes(BaseRoutes):
    """
        Wallet pin routes
        api/v1/<wallet_id>/pin/
    """
    @token_required
    def put(self, wallet_id):
        """
            handle Put method from
            api/v1/<wallet_id>/pin/
            update wallet pin
        """
        request_data = WalletUpdatePinRequestSchema.parser.parse_args(strict=True)
        try:
            wallet = UpdatePinSchema(strict=True).validate(request_data)
        except ValidationError as error:
            raise BadRequest(self.error_response["INVALID_PARAMETER"]["TITLE"],
                             self.error_response["INVALID_PARAMETER"]["MESSAGE"],
                             error.messages)
        response = WalletServices(wallet_id).update_pin(request_data)
        return response
    #end def

    @token_required
    def post(self, wallet_id):
        """
            handle POST method from
            api/v1/<wallet_id>/pin/
            update wallet pin
        """
        request_data = PinOnlyRequestSchema.parser.parse_args(strict=True)
        try:
            excluded = ("id", "wallet_id", "balance", "transaction_type",
                        "notes", "payment_details", "created_at", "amount")
            transfer = TransactionSchema(strict=True).validate(request_data,
                                                               partial=excluded)
        except ValidationError as error:
            raise BadRequest(self.error_response["INVALID_PARAMETER"]["TITLE"],
                             self.error_response["INVALID_PARAMETER"]["MESSAGE"],
                             error.messages)
        # need to serialize here
        response = WalletServices(wallet_id, request_data["pin"]).check()
        return response
    #end def
#end class

@api.route('/<string:wallet_id>/forgot/')
class WalletForgotPinRoutes(BaseRoutes):
    """
        Wallet Forgot Pin ROutes
        api/v1/<wallet_id>/forgot/
    """
    @token_required
    def get(self, wallet_id):
        """
            handle GET method from
            api/v1/<wallet_id>/forgot/
            send forgot pin otp via sms
        """
        response = WalletServices(wallet_id).send_forgot_otp()
        return response
    #end def

    @token_required
    def post(self, wallet_id):
        """
            handle POST method from
            api/v1/<wallet_id>/forgot/
            verify forgot pin
        """
        request_data = ForgotPinRequestSchema.parser.parse_args(strict=True)
        # need to serialize here
        response = WalletServices(wallet_id).verify_forgot_otp(request_data)
        return response
    #end def
#end class

@api.route('/<string:wallet_id>/withdraw/')
class WalletWithdrawRoutes(BaseRoutes):
    """
        Wallet Withdraw Routes
        api/v1/<wallet_id>/withdraw/
    """
    @token_required
    def post(self, wallet_id):
        """
            handle POST method from
            api/v1/<wallet_id>/withdraw/
            withdraw money
        """
        request_data = WithdrawRequestSchema.parser.parse_args(strict=True)
        try:
            excluded = ("id", "wallet_id", "balance", "transaction_type",
                        "notes", "payment_details", "created_at")
            transfer = TransactionSchema(strict=True).validate(request_data)
        except ValidationError as error:
            raise BadRequest(self.error_response["INVALID_PARAMETER"]["TITLE"],
                             self.error_response["INVALID_PARAMETER"]["MESSAGE"],
                             error.messages)
        #end try
        request_data["bank_name"] = "BNI"
        response = WithdrawServices(wallet_id,
                                    request_data["pin"]).request(request_data)
        return response
    #end def
#end class

@api.route('/<string:source_wallet_id>/transfer/checkout')
class WalletCheckoutRoutes(BaseRoutes):
    """
        Wallet Checkout Routes
        api/v1/<source>/transfer/checkout
    """
    @token_required
    def post(self, source_wallet_id):
        """
            handle POST method from
            api/v1/<source>/transfer/checkout
            checkout user wallets using phone number
        """
        # parse request data
        request_data = TransferCheckoutRequestSchema.parser.parse_args(strict=True)
        try:
            excluded = "username", "name", "pin", "password", "role", "email"
            transfer = UserSchema(strict=True).validate(request_data,
                                                        partial=(excluded))
        except ValidationError as error:
            raise BadRequest(self.error_response["INVALID_PARAMETER"]["TITLE"],
                             self.error_response["INVALID_PARAMETER"]["MESSAGE"],
                             error.messages)
        #end if
        response = TransferServices().checkout(request_data["phone_ext"], request_data["phone_number"])
        return response
    #end def
#end class

################################## PATCH ############################################
@api.route('/transfer/checkout2')
class WalletCheckout2Routes(BaseRoutes):
    """
        Wallet Checkout Routes
        api/v1/<source>/transfer/checkout
    """
    @api_key_required
    def post(self):
        """
            handle POST method from
            api/v1/<source>/transfer/checkout
            checkout user wallets using phone number
        """
        # parse request data
        request_data = TransferCheckoutRequestSchema.parser.parse_args(strict=True)
        try:
            excluded = "username", "name", "pin", "password", "role", "email"
            transfer = UserSchema(strict=True).validate(request_data,
                                                        partial=(excluded))
        except ValidationError as error:
            raise BadRequest(self.error_response["INVALID_PARAMETER"]["TITLE"],
                             self.error_response["INVALID_PARAMETER"]["MESSAGE"],
                             error.messages)
        #end if
        response = TransferServices().checkout2(request_data["phone_ext"], request_data["phone_number"])
        return response
    #end def
#end class

@api.route('/<string:source_wallet_id>/transfer/<string:destination_wallet_id>')
class WalletTransferRoutes(BaseRoutes):
    """
        Wallet Transfer Routes
        api/v1/<source>/transfer/<destination>
    """
    @token_required
    def post(self, source_wallet_id, destination_wallet_id):
        """
            handle POST method from
            api/v1/<source>/transfer/<destination>
            send money between VA
        """
        # parse request data
        request_data = TransferRequestSchema.parser.parse_args(strict=True)
        try:
            excluded = ("id", "wallet_id", "balance", "transaction_type",
                        "notes", "payment_details", "created_at")
            transfer = TransactionSchema(strict=True).validate(request_data,
                                                               partial=excluded)
        except ValidationError as error:
            raise BadRequest(self.error_response["INVALID_PARAMETER"]["TITLE"],
                             self.error_response["INVALID_PARAMETER"]["MESSAGE"],
                             error.messages)
        #end if
        response = TransferServices(source_wallet_id,
                                    request_data["pin"],
                                    destination_wallet_id).internal_transfer(request_data)
        return response
    #end def
#end class

@api.route('/<string:source_wallet_id>/transfer/bank/<string:bank_account_id>')
class WalletBankTransferRoutes(BaseRoutes):
    """
        Wallet Bank Transfer Routes
        api/v1/source/transfer/bank/<bank_account_id>
    """
    @token_required
    def post(self, source_wallet_id, bank_account_id):
        """
            handle POST method from
            api/v1/<source>/transfer/bank/<bank_account_id>
            send money to bank account
        """
        # parse request data
        request_data = TransferRequestSchema.parser.parse_args(strict=True)
        try:
            excluded = ("id", "wallet_id", "balance", "transaction_type",
                        "payment_details", "created_at")
            transfer = TransactionSchema(strict=True).validate(request_data,
                                                               partial=excluded)
        except ValidationError as error:
            raise BadRequest(self.error_response["INVALID_PARAMETER"]["TITLE"],
                             self.error_response["INVALID_PARAMETER"]["MESSAGE"],
                             error.messages)
        #end if

        request_data["destination"] = bank_account_id
        response = TransferServices(source_wallet_id,
                                    request_data["pin"]).external_transfer(request_data)
        return response
    #end def
#end class

################################## PATCH ############################################
@api.route('/<string:source_wallet_id>/transfer/bank2/<string:bank_account_id>')
class WalletBankTransfer2Routes(BaseRoutes):
    """
        Wallet Bank Transfer Routes
        api/v1/source/transfer/bank/<bank_account_id>
    """
    @api_key_required
    def post(self, source_wallet_id, bank_account_id):
        """
            handle POST method from
            api/v1/<source>/transfer/bank/<bank_account_id>
            send money to bank account
        """
        # parse request data
        request_data = TransferRequestSchema.parser.parse_args(strict=True)
        try:
            excluded = ("id", "wallet_id", "balance", "transaction_type",
                        "payment_details", "created_at")
            transfer = TransactionSchema(strict=True).validate(request_data,
                                                               partial=excluded)
        except ValidationError as error:
            raise BadRequest(self.error_response["INVALID_PARAMETER"]["TITLE"],
                             self.error_response["INVALID_PARAMETER"]["MESSAGE"],
                             error.messages)
        #end if

        request_data["destination"] = bank_account_id
        response = TransferServices(source_wallet_id,
                                    request_data["pin"]).external_transfer(request_data)
        return response
    #end def
#end class

