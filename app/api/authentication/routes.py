from functools import wraps
import traceback

from flask              import request, jsonify
from flask_restplus     import Resource
from flask_jwt_extended import jwt_refresh_token_required, jwt_required, get_jwt_identity, get_raw_jwt, verify_jwt_in_request, get_jwt_claims
from flask_jwt_extended.exceptions import RevokedTokenError

from app.api.authentication         import api
from app.api.serializer             import UserSchema
from app.api.request_schema         import AuthRequestSchema
from app.api.errors                 import bad_request, internal_error
from app.api.authentication.modules import authentication
from app.api.models                 import BlacklistToken, User, Wallet, Role
from app.api.config                 import config

request_schema = AuthRequestSchema.parser

RESPONSE_MSG = config.Config.RESPONSE_MSG

"""
    AUTH API
"""

@api.route("/token")
class AccessTokenLogin(Resource):
    # authenticate the user and return access token
    def post(self):
        request_data = request_schema.parse_args(strict=True)
        data = {
            "username"   : request_data["username"],
            "password"   : request_data["password"],
        }

        # request data validator
        errors = UserSchema().validate(data, partial=("name","phone_ext","phone_number","pin","role","email"))
        if errors:
            return bad_request(errors)
        #end if

        response = authentication.AuthController().create_token(data)
        return response
#end def

@api.route("/refresh")
class RefreshTokenLogin(Resource):
    # refresh the token
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()

        response = authentication.AuthController().refresh_token(current_user)
        return response
    #end def
#end class

@api.route("/token/revoke")
class AccessTokenLogout(Resource):
    # blacklist access token
    @jwt_required
    def post(self):
        token = get_raw_jwt()["jti"]
        response = authentication.AuthController().logout_access_token(token)

        return response
    #end def
#end class

@api.route("/refresh/revoke")
class RefreshTokenLogout(Resource):
    # blacklist refresh token
    @jwt_refresh_token_required
    def post(self):
        token = get_raw_jwt()["jti"]
        response = authentication.AuthController().logout_refresh_token(token)

        return response
    #end def
#end class


