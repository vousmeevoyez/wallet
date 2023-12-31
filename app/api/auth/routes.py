"""
    Authentication Routes
    _____________________
    Module that handler routes for authentication
"""
# pylint: disable=bad-continuation
# pylint: disable=too-few-public-methods
# pylint: disable=no-self-use
# pylint: disable=no-name-in-module

# local
from app.api.auth import api

from app.lib.core import Routes

# services
from app.api.auth.modules.auth_services import AuthServices

# serializer
from app.api.serializer import UserSchema

# request schema
from app.api.request_schema import AuthRequestSchema

# decorator
from app.api.auth.decorator import (
    refresh_token_only,
    token_required,
    get_current_token,
    get_token_payload,
)


@api.route("/token")
class TokenRoutes(Routes):
    """
        Access Token
        /auth/token
    """

    __schema__ = AuthRequestSchema
    __serializer__ = UserSchema(only=("username", "password"))

    def post(self):
        """
            Handle POST Method
            Endpoint for getting access token using username and password
        """
        response = AuthServices().create_token(self.serialize(self.payload()))
        return response


# end def


@api.route("/refresh")
class RefreshTokenRoutes(Routes):
    """
        Refresh Token
        /auth/refresh
    """

    # refresh the token
    @refresh_token_only
    def post(self):
        """
            Handle POST Method
            Endpoint for refreshing token
        """
        payload = get_token_payload()
        response = AuthServices().refresh_token(payload["user"])
        return response

    # end def


# end class


@api.route("/token/revoke")
class TokenRevokeRoutes(Routes):
    """
        Refresh Token
        /auth/token/revoke
    """

    @token_required
    def post(self):
        """
            Handle POST Method
            Endpoint for revoking access token
        """
        # fetch token from header
        token = get_current_token()
        response = AuthServices().logout(token)
        return response

    # end def


# end class
