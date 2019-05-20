"""
    Authentication Routes
    _____________________
    Module that handler routes for authentication
"""
# pylint: disable=bad-continuation
# pylint: disable=too-few-public-methods
# pylint: disable=no-self-use
# pylint: disable=no-name-in-module

# external
from flask_restplus import Resource #pylint: disable=import-error
# local
from app.api.auth import api
# services
from app.api.auth.modules.auth_services import AuthServices
# serializer
from app.api.serializer import UserSchema
# request schema
from app.api.request_schema import AuthRequestSchema
# decorator
from app.api.auth.decorator import refresh_token_only
from app.api.auth.decorator import token_required
from app.api.auth.decorator import get_current_token
from app.api.auth.decorator import get_token_payload
# http error
from app.api.error.http import BadRequest
# configuration
from app.config import config

class BaseRoutes(Resource):
    """ base routes class"""
    error_response = config.Config.ERROR_CONFIG
# end class

@api.route("/token")
class TokenRoutes(BaseRoutes):
    """
        Access Token
        /auth/token
    """
    def post(self):
        """ Endpoint for getting access token using username and password """
        request_data = AuthRequestSchema.parser.parse_args()

        excluded = "name", "phone_ext", "phone_number", "pin", "role", "email"
        errors = UserSchema().validate(request_data, partial=(excluded))
        if errors:
            raise BadRequest(self.error_response["INVALID_PARAMETER"]["TITLE"],
                             self.error_response["INVALID_PARAMETER"]["MESSAGE"], errors)
        #end if

        response = AuthServices().create_token(request_data)
        return response
#end def

@api.route("/refresh")
class RefreshTokenRoutes(BaseRoutes):
    """
        Refresh Token
        /auth/refresh
    """
    # refresh the token
    @refresh_token_only
    def post(self):
        """ Endpoint for refreshing token """
        payload = get_token_payload()
        response = AuthServices().refresh_token(payload["user"])
        return response
    #end def
#end class

@api.route("/token/revoke")
class TokenRevokeRoutes(BaseRoutes):
    """
        Refresh Token
        /auth/token/revoke
    """
    @token_required
    def post(self):
        """ Endpoint for revoking access token """
        # fetch token from header
        token = get_current_token()
        response = AuthServices().logout(token)
        return response
    #end def
#end class
