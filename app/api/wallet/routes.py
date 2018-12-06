import traceback

from flask_jwt_extended import jwt_refresh_token_required, jwt_required, get_jwt_identity, get_jwt_claims, get_raw_jwt
from flask_restplus     import Resource

from app.api.wallet             import api
from app.api.serializer         import WalletSchema
from app.api.request_schema     import WalletRequestSchema
from app.api.errors             import bad_request, internal_error, request_not_found

from app.api.wallet.modules     import wallet
from app.api.authentication.decorator import admin_required

from app.api.config             import config

RESPONSE_MSG = config.Config.RESPONSE_MSG

request_schema = WalletRequestSchema.parser

@api.route('/<int:wallet_id>')
class WalletDetails(Resource):
    @jwt_required
    def get(self, wallet_id):
        response = wallet.WalletController().details({ "id" : wallet_id })
        return response
    #end def
#end class

@api.route('/<int:wallet_id>/balance/')
class WalletBalance(Resource):
    @jwt_required
    def get(self, wallet_id):
        response = wallet.WalletController().check_balance({ "id" : wallet_id })
        return response
    #end def
#end class

@api.route('/<int:user_id>')
class CreateWallet(Resource):
    @jwt_required
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
