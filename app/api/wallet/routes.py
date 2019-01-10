"""
    Wallet Routes
    _______________
    this is module that handle rquest from url and then forward it to services
"""
from flask_restplus     import Resource

from app.api.wallet             import api
from app.api.serializer         import WalletSchema, TransactionSchema
from app.api.request_schema     import WalletRequestSchema, WalletUpdatePinRequestSchema, PinAuthRequestSchema, ForgotPinRequestSchema, TransferRequestSchema
from app.api.errors             import bad_request, internal_error, request_not_found

# wallet modules
from app.api.wallet.modules.wallet_services import WalletServices
from app.api.wallet.modules.transfer_services import TransferServices

# authentication
from app.api.authentication.decorator import refresh_token_only, token_required, get_current_token, get_token_payload, admin_required
from app.api.authentication.helper import AuthenticationHelper

from app.api.config             import config

RESPONSE_MSG = config.Config.RESPONSE_MSG

# REQUEST SCHEMA HERE
request_schema = WalletRequestSchema.parser
update_pin_request_schema = WalletUpdatePinRequestSchema.parser
pin_auth_request_schema = PinAuthRequestSchema.parser
forgot_pin_request_schema = ForgotPinRequestSchema.parser
transfer_request_schema = TransferRequestSchema.parser

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
        response = WalletServices().history(wallet_id)
        return response
    #end def
#end class

@api.route('/<int:wallet_id>/transactions/<int:transaction_id>')
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
        data = {
            "source"      : source_wallet_id,
            "destination" : destination_wallet_id,
            "amount"      : request_data["amount"],
            "notes"       : request_data["notes"],
            "pin"         : request_data["pin"],
        }

        # checking token identity to make sure user can only access their wallet information
        auth_resp = AuthenticationHelper().check_wallet_permission(payload_resp["user_id"],\
                                             source_wallet_id)
        if auth_resp is not None:
            return auth_resp
        #end if

        # request data validator
        errors = TransactionSchema().validate(data)
        if errors:
            return bad_request(errors)
        #end if

        response = TransferServices().internal_transfer(data)
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
        data = {
            "source"      : source_wallet_id,
            "destination" : bank_account_id,
            "amount"      : request_data["amount"],
            "notes"       : request_data["notes"],
            "pin"         : request_data["pin"],
        }

        # checking token identity to make sure user can only access their wallet information
        auth_resp = AuthenticationHelper().check_wallet_permission(payload_resp["user_id"],\
                                                       source_wallet_id)
        if auth_resp is not None:
            return auth_resp
        #end if

        # request data validator
        errors = TransactionSchema().validate(data)
        if errors:
            return bad_request(errors)
        #end if

        response = TransferServices().external_transfer(data)
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
        data = {
            "name"   : request_data["name"],
            "msisdn" : request_data["msisdn"],
            "pin"    : request_data["pin"],
            "user_id": user_id,
        }

        response = WalletServices().add(data)
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
