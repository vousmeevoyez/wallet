from functools import wraps
import traceback

from flask_restplus     import Resource, reqparse

from app.api.authentication           import api
from app.api.serializer               import UserSchema
from app.api.request_schema           import AuthRequestSchema
from app.api.errors                   import bad_request, internal_error
from app.api.authentication.modules   import authentication
from app.api.authentication.decorator import refresh_token_only, token_required, get_current_token, get_token_payload
from app.api.config                   import config

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
    @refresh_token_only
    def post(self):
        # fetch payload
        payload_resp = get_token_payload()
        if not isinstance(payload_resp, dict):
            return payload_resp
        #end if

        current_user = payload_resp["user_id"]

        response = authentication.AuthController().refresh_token(current_user)
        return response
    #end def
#end class

@api.route("/token/revoke")
class AccessTokenLogout(Resource):
    # blacklist access token
    @token_required
    def post(self):
        # fetch token from header
        token = get_current_token()

        response = authentication.AuthController().logout_access_token(token)
        return response
    #end def
#end class

@api.route("/refresh/revoke")
class RefreshTokenLogout(Resource):
    # blacklist refresh token
    @refresh_token_only
    def post(self):
        # fetch token from header
        token = get_current_token()

        response = authentication.AuthController().logout_refresh_token(token)
        return response
    #end def
#end class