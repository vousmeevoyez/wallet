"""
    Authentication Routes
    _____________________
    Module that handler routes for authentication
"""
# pylint: disable=bad-continuation
# pylint: disable=too-few-public-methods
# pylint: disable=no-self-use

from flask_restplus import Resource #pylint: disable=import-error

from app.api.authentication import api
# services
from app.api.authentication.modules.auth_services   import AuthServices
# serializer
from app.api.serializer import UserSchema
# request schema
from app.api.request_schema import AuthRequestSchema
# http errors
from app.api.http_response import bad_request
from app.api.http_response import unauthorized
# custom decorator
from app.api.authentication.decorator import refresh_token_only
from app.api.authentication.decorator import token_required
from app.api.authentication.decorator import get_current_token
from app.api.authentication.decorator import get_token_payload
# exceptions
from app.api.exception.general import SerializeError
from app.api.exception.general import RecordNotFoundError
from app.api.exception.general import CommitError

from app.api.exception.authentication import TokenError
from app.api.exception.authentication import InvalidCredentialsError
from app.api.exception.authentication import InvalidAuthorizationError
from app.api.exception.authentication import FailedRevokedTokenError

from app.api.exception.user import UserNotFoundError

REQUEST_SCHEMA = AuthRequestSchema.parser

@api.route("/token")
class TokenRoutes(Resource):
    """
        Access Token Routes
        api/v1/token/
    """
    # authenticate the user and return access token
    def post(self):
        """
            handle POST method from
            api/v1/token/
            return access token
        """
        request_data = REQUEST_SCHEMA.parse_args(strict=True)

        # request data validator
        excluded = "name", "phone_ext", "phone_number", "pin", "role", "email"
        errors = UserSchema().validate(request_data, partial=(excluded))
        if errors:
            raise SerializeError(errors)
        #end if

        try:
            response = AuthServices().create_token(request_data)
        except UserNotFoundError as error:
            raise RecordNotFoundError(error.msg, error.title)
        except InvalidCredentialsError as error:
            raise InvalidCredentialsError(error.msg, error.title)
        return response
#end def

@api.route("/refresh")
class RefreshTokenRoutes(Resource):
    """
        refresh Token Routes
        api/v1/refresh/
    """
    # refresh the token
    @refresh_token_only
    def post(self):
        """
            handle POST method from
            api/v1/refresh/
            return refresh token
        """
        # fetch payload
        try:
            payload = get_token_payload()
        except TokenError as error:
            raise InvalidAuthorizationError(error)
        #end try
        response = AuthServices().refresh_token(payload["user"])
        return response
    #end def
#end class

@api.route("/token/revoke")
class TokenRevokeRoutes(Resource):
    """
        Access Token Revoke Routes
        api/v1/token/revoke
    """
    # blacklist access token
    @token_required
    def post(self):
        """
            handle POST method from
            api/v1/token/revoke
            blacklist the token
        """
        # fetch token from header
        try:
            token = get_current_token()
        except TokenError as error:
            raise InvalidAuthorizationError(error)
        #end try

        try:
            response = AuthServices().logout_access_token(token)
        except FailedRevokedTokenError as error:
            raise CommitError(error.msg)
        #end try
        return response
    #end def
#end class

@api.route("/refresh/revoke")
class RefreshTokenRevokeRoutes(Resource):
    """
        refresg Token Revoke Routes
        api/v1/refresh/revoke
    """
    # blacklist refresh token
    @refresh_token_only
    def post(self):
        """
            handle POST method from
            api/v1/refresh/revoke
            blacklist the token
        """
        # fetch token from header
        try:
            token = get_current_token()
        except TokenError as error:
            raise InvalidAuthorizationError(error)
        #end try
        try:
            response = AuthServices().logout_refresh_token(token)
        except FailedRevokedTokenError as error:
            raise CommitError(error.msg)
        #end try
        return response
    #end def
#end class
