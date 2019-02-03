"""
    Auth Services
    _________________
    This services module to handle all incoming authenticaion
"""

from sqlalchemy.exc import IntegrityError

# database
from app.api import db
# models
from app.api.models import User, BlacklistToken
# http response
from app.api.http_response import bad_request
from app.api.http_response import unauthorized
from app.api.http_response import request_not_found
from app.api.http_response import no_content
from app.api.http_response import unprocessable_entity
# exceptions
from app.api.exception.authentication.exceptions import RevokedTokenError
from app.api.exception.authentication.exceptions import SignatureExpiredError
from app.api.exception.authentication.exceptions import InvalidTokenError
from app.api.exception.authentication.exceptions import TokenError
from app.api.exception.authentication.exceptions import EmptyPayloadError
# configuration
from app.config import config

RESPONSE_MSG = config.Config.RESPONSE_MSG

class AuthServices:
    """ Authentication Services Class"""

    @staticmethod
    def _create_access_token(user):
        """ get user object and then create access token"""
        token = User.encode_token("ACCESS", user.id, user.role.description)
        return token.decode()
    #end def

    @staticmethod
    def _create_refresh_token(user):
        """ get user object and then create refresh token"""
        token = User.encode_token("REFRESH", user.id, user.role.description)
        return token.decode()
    #end def

    @staticmethod
    def current_login_user(token):
        """
            function to check who is currently login by ddecode their token
            args:
                token -- jwt token
        """
        try:
            payload = User.decode_token(token)
        except RevokedTokenError:
            raise TokenError("Revoked Token")
        except SignatureExpiredError:
            raise TokenError("Signature Expired")
        except InvalidTokenError:
            raise TokenError("Invalid Token")
        except EmptyPayloadError:
            raise TokenError("Empty Payload")

        # fetch user information
        response = {
            "token_type": payload["type"],
            "user_id"   : payload["sub"],
            "role"      : payload["role"],
        }
        return response
    #end def

    def create_token(self, params):
        """
            Function to create jwt token
            args:
                params -- parameter
        """
        username = params["username"]
        password = params["password"]

        user = User.query.filter_by(username=username).first()
        if user is None:
            return request_not_found()
        #end if

        if user.check_password(password) is not True:
            return unauthorized("Invalid Credentials")
        #end if

        # generate token here
        access_token = self._create_access_token(user)
        refresh_token = self._create_refresh_token(user)

        response = {
            "access_token" : access_token,
            "refresh_token": refresh_token
        }
        return response
    #end def

    def refresh_token(self, current_user):
        """
            Function to create refresh token
            args:
                current_user -- get current user id
        """
        response = {}

        user = User.query.filter_by(id=current_user).first()
        if user is None:
            return request_not_found()
        #end if

        access_token = self._create_access_token(user)

        response = {
            "access_token" : access_token,
        }
        return response
    #end def

    def logout_access_token(self, token):
        """
            Function to logout access token and blacklist the token
            args:
                token -- access token
        """
        # decode the token first
        try:
            payload = User.decode_token(token)
        except RevokedTokenError:
            return unauthorized("Revoked Token")
        except SignatureExpiredError:
            return unauthorized("Signature Expired")
        except InvalidTokenError:
            return unauthorized("Invalid Token")
        except EmptyPayloadError:
            return unauthorized("Empty Payload")
        #end try

        blacklist_token = BlacklistToken(token=token)

        try:
            db.session.add(blacklist_token)
            db.session.commit()
        except IntegrityError as error:
            return unprocessable_entity("Failed logging out token")
        #end try
        return no_content()
    #end def

    def logout_refresh_token(self, token):
        """
            Function to logout refresh token and blacklist the token
            args:
                token -- refresh token
        """
        # decode the token first
        try:
            payload = User.decode_token(token)
        except RevokedTokenError:
            return unauthorized("Revoked Token")
        except SignatureExpiredError:
            return unauthorized("Signature Expired")
        except InvalidTokenError:
            return unauthorized("Invalid Token")
        except EmptyPayloadError:
            return unauthorized("Empty Payload")

        blacklist_token = BlacklistToken(token=token)

        try:
            db.session.add(blacklist_token)
            db.session.commit()
        except IntegrityError as error:
            return unprocessable_entity("Failed logging out token")
        #end try
        return no_content()
    #end def
#end class
