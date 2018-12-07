# python 
import traceback

from flask_restplus     import Resource

from app.api.wallet             import api
from app.api.serializer         import WalletSchema, TransactionSchema
from app.api.request_schema     import WalletRequestSchema, WalletUpdatePinRequestSchema, PinAuthRequestSchema, ForgotPinRequestSchema, TransferRequestSchema
from app.api.errors             import bad_request, internal_error, request_not_found

# wallet modules
from app.api.wallet.modules     import wallet
from app.api.wallet.modules     import transfer

# authentication 
from app.api.authentication.decorator import refresh_token_only, token_required, get_current_token, get_token_payload, admin_required
from app.api.authentication           import helper as auth_helper

from app.api.config             import config

RESPONSE_MSG = config.Config.RESPONSE_MSG

# REQUEST SCHEMA HERE
request_schema            = WalletRequestSchema.parser
update_pin_request_schema = WalletUpdatePinRequestSchema.parser
pin_auth_request_schema   = PinAuthRequestSchema.parser
forgot_pin_request_schema = ForgotPinRequestSchema.parser
transfer_request_schema   = TransferRequestSchema.parser

@api.route('/<int:wallet_id>')
class WalletDetails(Resource):
    @token_required
    def get(self, wallet_id):
        # fetch payload
        payload_resp = get_token_payload()
        if not isinstance(payload_resp, dict):
            return payload_resp
        #end if

        # checking token identity to make sure user can only access their wallet information
        permission_response = auth_helper.AuthenticationHelper().check_wallet_permission(payload_resp["user_id"], wallet_id)
        if permission_response != None:
            return permission_response
        #end if

        response = wallet.WalletController().details({ "id" : wallet_id })
        return response
    #end def
#end class

@api.route('/<int:wallet_id>/balance/')
class WalletBalance(Resource):
    @token_required
    def post(self, wallet_id):
        request_data = pin_auth_request_schema.parse_args(strict=True)
        data = {
            "pin" : request_data["pin"],
        }

        # serialize input here
        errors = WalletSchema().validate(data, partial=("user_id","created_at"))
        if errors:
            return bad_request(errors)
        #end if

        data["id"] = wallet_id

        response = wallet.WalletController().check_balance(data)
        return response
    #end def
#end class

@api.route('/<int:wallet_id>/transactions/')
class WalletTransaction(Resource):
    @token_required
    def get(self, wallet_id):
        response = wallet.WalletController().history(wallet_id)
        return response
    #end def
#end class

@api.route('/<int:wallet_id>/pin/')
class UpdateWalletPin(Resource):
    @token_required
    def put(self, wallet_id):
        request_data = update_pin_request_schema.parse_args(strict=True)
        data = {
            "pin"         : request_data["pin"],
            "confirm_pin" : request_data["confirm_pin"],
            "id"          : wallet_id
        }
        # need to serialize here
        response = wallet.WalletController().update_pin(data)
        return response
    #end def
#end class

@api.route('/<int:wallet_id>/forgot/')
class ForgotWalletPin(Resource):
    @token_required
    def get(self, wallet_id):
        response = wallet.WalletController().send_forgot_otp(wallet_id)
        return response
    #end def

    @token_required
    def post(self, wallet_id):
        request_data = forgot_pin_request_schema.parse_args(strict=True)
        data = {
            "pin"         : request_data["pin"],
            "otp_code"    : request_data["otp_code"],
            "otp_key"     : request_data["otp_key"],
            "id"          : wallet_id,
        }
        # need to serialize here
        response = wallet.WalletController().verify_forgot_otp(data)
        return response
    #end def
#end class

@api.route('/<int:source_wallet_id>/transfer/<int:destination_wallet_id>')
class WalletTransfer(Resource):
    @token_required
    def post(self, source_wallet_id, destination_wallet_id):
        # fetch payload
        payload_resp = get_token_payload()
        if not isinstance(payload_resp, dict):
            return payload_resp
        #end if

        # parse request data
        request_data = transfer_request_schema.parse_args(strict=True)
        data = {
            "source"      : source_wallet_id,
            "destination" : destination,
            "amount"      : request_data["amount"],
            "notes"       : request_data["notes"],
            "pin"         : request_data["pin"],
        }

        # checking token identity to make sure user can only access their wallet information
        permission_response = auth_helper.AuthenticationHelper().check_wallet_permission(payload_resp["user_id"], source_wallet_id)
        if permission_response != None:
            return permission_response
        #end if

        # request data validator
        errors = TransactionSchema().validate(data)
        if errors:
            return bad_request(errors)
        #end if

        response = transfer.TransferController().internal_transfer(data)
        return response
    #end def
#end class

@api.route('/<int:user_id>')
class CreateWallet(Resource):
    @admin_required
    def post(self, user_id):
        request_data = request_schema.parse_args(strict=True)
        data = {
            "name"   : request_data["name"   ],
            "msisdn" : request_data["msisdn" ],
            "pin"    : request_data["pin"    ],
            "user_id": user_id,
        }

        response = wallet.WalletController().create(data)
        return response
    #end def
#end class

@api.route('/')
class WalletList(Resource):
    @admin_required
    def get(self):
        response = wallet.WalletController().all()
        return response
    #end def
#end class
