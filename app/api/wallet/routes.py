"""
    Wallet Routes
    _______________
    this is module that handle rquest from url and then forward it to services
"""
#pylint: disable=import-error
#pylint: disable=invalid-name
#pylint: disable=no-self-use
#pylint: disable=too-few-public-methods

from flask_restplus     import Resource

from app.api.wallet import api
#serializer
from app.api.serializer import WalletSchema
from app.api.serializer import TransactionSchema
from app.api.serializer import WalletTransactionSchema
# request schema
from app.api.request_schema import WalletRequestSchema
from app.api.request_schema import WalletUpdatePinRequestSchema
from app.api.request_schema import PinAuthRequestSchema
from app.api.request_schema import ForgotPinRequestSchema
from app.api.request_schema import TransferRequestSchema
from app.api.request_schema import WalletTransactionRequestSchema
from app.api.request_schema import QRTransferRequestSchema

#http errors
from app.api.errors import bad_request

# wallet modules
from app.api.wallet.modules.wallet_services import WalletServices
from app.api.wallet.modules.transfer_services import TransferServices

# authentication
from app.api.authentication.decorator import token_required
from app.api.authentication.decorator import get_token_payload
from app.api.authentication.decorator import admin_required
# helper
from app.api.authentication.helper import AuthenticationHelper
# configuration
from app.api.config import config

RESPONSE_MSG = config.Config.RESPONSE_MSG

# REQUEST SCHEMA HERE
request_schema = WalletRequestSchema.parser
update_pin_request_schema = WalletUpdatePinRequestSchema.parser
pin_auth_request_schema = PinAuthRequestSchema.parser
forgot_pin_request_schema = ForgotPinRequestSchema.parser
transfer_request_schema = TransferRequestSchema.parser
wallet_transaction_request_schema = WalletTransactionRequestSchema.parser
qr_transfer_request_schema = QRTransferRequestSchema.parser

@api.route('/<int:wallet_id>')
class WalletRoutes(Resource):
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
        # fetch payload
        payload_resp = get_token_payload()
        if not isinstance(payload_resp, dict):
            return payload_resp
        #end if

        # checking token identity to make sure user can only access their wallet information
        auth_resp = AuthenticationHelper().check_wallet_permission(payload_resp["user_id"],\
                                             wallet_id)
        if auth_resp is None:
            return auth_resp
        #end if

        response = WalletServices().info({"id" : wallet_id})
        return response
    #end def
#end class

@api.route('/<int:wallet_id>/qr/')
class WalletQrRoutes(Resource):
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
        response = WalletServices().get_qr({"id" : wallet_id})
        return response
    #end def
#end class

@api.route('/<int:wallet_id>/qr/transfer')
class WalletQrTransferRoutes(Resource):
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
        request_data = qr_transfer_request_schema.parse_args(strict=True)
        errors = TransactionSchema().validate(request_data)
        if errors:
            return bad_request(errors)
        #end if
        request_data["source"] = wallet_id
        response = TransferServices().qr_transfer(request_data)
        return response
    #end def
#end class

@api.route('/<int:wallet_id>/balance/')
class WalletBalanceRoutes(Resource):
    """
        Wallet Balance Routes
        api/v1/<wallet_id>/balance
    """
    @token_required
    def post(self, wallet_id):
        """
            handle GET method from
            api/v1/<wallet_id>/balance
            return wallet balance
        """
        request_data = pin_auth_request_schema.parse_args(strict=True)
        data = {
            "pin" : request_data["pin"],
        }

        # serialize input here
        errors = WalletSchema().validate(data, partial=("user_id", "created_at"))
        if errors:
            return bad_request(errors)
        #end if

        data["id"] = wallet_id

        response = WalletServices().check_balance(data)
        return response
    #end def
#end class

@api.route('/<int:wallet_id>/transactions')
class WalletTransactionRoutes(Resource):
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
        request_data = wallet_transaction_request_schema.parse_args(strict=True)

        errors = WalletTransactionSchema().validate(request_data)
        if errors:
            return bad_request(errors)
        #end if
        request_data["wallet_id"] = wallet_id
        response = WalletServices().history(request_data)
        return response
    #end def
#end class

@api.route('/<int:wallet_id>/transactions/<transaction_id>')
class WalletTransactionDetailsRoutes(Resource):
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
        response = WalletServices().history_details(wallet_id, transaction_id)
        return response
    #end def
#end class

@api.route('/<int:wallet_id>/pin/')
class WalletPinRoutes(Resource):
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
        request_data = update_pin_request_schema.parse_args(strict=True)
        data = {
            "old_pin"     : request_data["old_pin"],
            "pin"         : request_data["pin"],
            "confirm_pin" : request_data["confirm_pin"],
            "id"          : wallet_id
        }
        # need to serialize here
        response = WalletServices().update_pin(data)
        return response
    #end def
#end class

@api.route('/<int:wallet_id>/forgot/')
class WalletForgotPinRoutes(Resource):
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
        response = WalletServices().send_forgot_otp(wallet_id)
        return response
    #end def

    @token_required
    def post(self, wallet_id):
        """
            handle POST method from
            api/v1/<wallet_id>/forgot/
            verify forgot pin
        """
        request_data = forgot_pin_request_schema.parse_args(strict=True)
        data = {
            "pin"      : request_data["pin"],
            "otp_code" : request_data["otp_code"],
            "otp_key"  : request_data["otp_key"],
            "id"       : wallet_id,
        }
        # need to serialize here
        response = WalletServices().verify_forgot_otp(data)
        return response
    #end def
#end class

@api.route('/<int:wallet_id>/withdraw/')
class WalletWithdrawRoutes(Resource):
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
        request_data = forgot_pin_request_schema.parse_args(strict=True)
        data = {
            "pin"    : request_data["pin"],
            "amount" : request_data["otp_key"],
            "id"     : wallet_id,
        }

        # need to serialize here
        response = WalletServices().request(data)
        return response
    #end def
#end class

@api.route('/<int:source_wallet_id>/transfer/<int:destination_wallet_id>')
class WalletTransferRoutes(Resource):
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
        # fetch payload
        payload_resp = get_token_payload()
        if not isinstance(payload_resp, dict):
            return payload_resp
        #end if

        # parse request data
        request_data = transfer_request_schema.parse_args(strict=True)
        request_data["source"] = source_wallet_id
        request_data["destination"] = destination_wallet_id

        # checking token identity to make sure user can only access their wallet information
        auth_resp = AuthenticationHelper().check_wallet_permission(payload_resp["user_id"],\
                                             source_wallet_id)
        if auth_resp is not None:
            return auth_resp
        #end if

        # request data validator
        errors = TransactionSchema().validate(request_data)
        if errors:
            return bad_request(errors)
        #end if

        response = TransferServices().internal_transfer(request_data)
        return response
    #end def
#end class

@api.route('/<int:source_wallet_id>/transfer/bank/<int:bank_account_id>')
class WalletBankTransferRoutes(Resource):
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
        # fetch payload
        payload_resp = get_token_payload()
        if not isinstance(payload_resp, dict):
            return payload_resp
        #end if

        # parse request data
        request_data = transfer_request_schema.parse_args(strict=True)
        request_data["source"] = source_wallet_id
        request_data["destination"] = bank_account_id

        # checking token identity to make sure user can only access their wallet information
        auth_resp = AuthenticationHelper().check_wallet_permission(payload_resp["user_id"],\
                                                       source_wallet_id)
        if auth_resp is not None:
            return auth_resp
        #end if

        # request data validator
        errors = TransactionSchema().validate(request_data)
        if errors:
            return bad_request(errors)
        #end if

        response = TransferServices().external_transfer(request_data)
        return response
    #end def
#end class

@api.route('/<int:user_id>')
class WalletAddRoutes(Resource):
    """
        Wallet add Routes
        api/v1/wallet/<user_id>
    """
    @admin_required
    def post(self, user_id):
        """
            Handle POST request from
            api/v1/wallet/<user_id>
        """
        request_data = request_schema.parse_args(strict=True)
        request_data["user_id"] = user_id

        response = WalletServices().add(request_data)
        return response
    #end def
#end class

@api.route('/')
class WalletListRoutes(Resource):
    """
        Wallet List Routes
        api/v1/wallet/
    """
    @admin_required
    def get(self):
        """
            Handle GET request from
            api/v1/wallet/
        """
        response = WalletServices().show()
        return response
    #end def
#end class
