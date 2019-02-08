"""
    Auth Services
    _________________
    This services module to handle all incoming authenticaion
"""

from sqlalchemy.exc import IntegrityError

# database
from app.api import db
# models
from app.api.models import User
from app.api.models import BlacklistToken
from app.api.models import Wallet
# exceptions
from app.api.exception.authentication import EmptyPayloadError
from app.api.exception.authentication import RevokedTokenError
from app.api.exception.authentication import SignatureExpiredError
from app.api.exception.authentication import InvalidTokenError
from app.api.exception.authentication import TokenError
from app.api.exception.authentication import InvalidCredentialsError

from app.api.exception.user import UserNotFoundError
from app.api.exception.authentication import FailedRevokedTokenError
from app.api.exception.general import RecordNotFoundError

# http response
from app.api.http_response import no_content
# configuration
from app.config import config

class AuthServices:
    """ Authentication Services Class"""

    @staticmethod
    def _create_access_token(user):
        """ get user object and then create access token"""
        token = User.encode_token("ACCESS", user.id)
        return token.decode()
    #end def

    @staticmethod
    def _create_refresh_token(user):
        """ get user object and then create refresh token"""
        token = User.encode_token("REFRESH", user.id)
        return token.decode()
    #end def

    @staticmethod
    def _current_login_user(token):
        """
            function to check who is currently login by decode their token
            used in decorator
            args:
                token -- jwt token
        """
        try:
            payload = User.decode_token(token)
        except RevokedTokenError:
            raise TokenError("Revoked Token")
        except SignatureExpiredError as error:
            #print(error)
            raise TokenError("Signature Expired")
        except InvalidTokenError as error:
            #print(error)
            raise TokenError("Invalid Token")
        except EmptyPayloadError:
            raise TokenError("Empty Payload")

        # fetch user information
        # convert user id to user object here
        user = User.query.filter_by(id=payload["sub"]).first()
        if user is None:
            raise RecordNotFoundError("User not Found", "USER_NOT_FOUND")

        response = {
            "token_type": payload["type"],
            "user"      : user,
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
            raise UserNotFoundError
        #end if

        if user.check_password(password) is not True:
            raise InvalidCredentialsError("Incorrect Credentials")
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
        access_token = self._create_access_token(current_user)
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
            payload = self._current_login_user(token)
        except TokenError as error:
            # catch and re rise to be captured by error handler
            raise TokenError(error)
        #end try
        blacklist_token = BlacklistToken(token=token)

        try:
            db.session.add(blacklist_token)
            db.session.commit()
        except IntegrityError as error:
            raise FailedRevokedTokenError("Failed logging out token", error)
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
            payload = self._current_login_user(token)
        except TokenError as error:
            # catch and re rise to be captured by error handler
            raise TokenError(error)
        #end try

        blacklist_token = BlacklistToken(token=token)

        try:
            db.session.add(blacklist_token)
            db.session.commit()
        except IntegrityError as error:
            raise FailedRevokedTokenError("Failed logging out token", error)
        #end try
        return no_content()
    #end def
#end class
