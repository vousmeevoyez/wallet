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
from app.api.error.authentication import RevokedTokenError
from app.api.error.authentication import SignatureExpiredError
from app.api.error.authentication import InvalidTokenError
from app.api.error.authentication import EmptyPayloadError

from app.api.error.http import *

# http response
from app.api.http_response import no_content
# configuration
from app.config import config

ERROR_CONFIG = config.Config.ERROR_CONFIG
STATUS_CONFIG = config.Config.STATUS_CONFIG

class AuthServices:
    """ Authentication Services Class"""

    @staticmethod
    def _create_token(user, token_type):
        """ get user object and then create access token"""
        token = User.encode_token(token_type, user.id)
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
            raise Unauthorized(ERROR_CONFIG["REVOKED_TOKEN"]["TITLE"],
                                  ERROR_CONFIG["REVOKED_TOKEN"]["MESSAGE"])
        except SignatureExpiredError as error:
            #print(error)
            raise Unauthorized(ERROR_CONFIG["SIGNATURE_EXPIRED"]["TITLE"],
                                  ERROR_CONFIG["SIGNATURE_EXPIRED"]["MESSAGE"])
        except InvalidTokenError as error:
            #print(error)
            raise Unauthorized(ERROR_CONFIG["INVALID_TOKEN"]["TITLE"],
                                  ERROR_CONFIG["INVALID_TOKEN"]["MESSAGE"])
        except EmptyPayloadError:
            raise Unauthorized(ERROR_CONFIG["EMPTY_PAYLOAD"]["TITLE"],
                                  ERROR_CONFIG["EMPTY_PAYLOAD"]["MESSAGE"])

        # fetch user information
        # convert user id to user object here
        user = User.query.filter_by(id=payload["sub"], 
                                    status=STATUS_CONFIG["ACTIVE"]).first()
        if user is None:
            raise RequestNotFound(ERROR_CONFIG["USER_NOT_FOUND"]["TITLE"],
                                  ERROR_CONFIG["USER_NOT_FOUND"]["MESSAGE"])

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
            raise RequestNotFound(ERROR_CONFIG["USER_NOT_FOUND"]["TITLE"],
                                  ERROR_CONFIG["USER_NOT_FOUND"]["MESSAGE"])
        #end if

        if user.check_password(password) is not True:
            raise Unauthorized(ERROR_CONFIG["INVALID_CREDENTIALS"]["TITLE"],
                               ERROR_CONFIG["INVALID_CREDENTIALS"]["MESSAGE"])
        #end if

        # generate token here
        access_token = self._create_token(user, "ACCESS")
        refresh_token = self._create_token(user, "REFRESH")

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
        access_token = self._create_token(current_user, "REFRESH")
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
        blacklist_token = BlacklistToken(token=token)
        try:
            db.session.add(blacklist_token)
            db.session.commit()
        except IntegrityError as error:
            raise UnprocessableEntity("REVOKE_FAILED", "Revoke Access Token \
                                      failed")
        #end try
        return no_content()
    #end def

    def logout_refresh_token(self, token):
        """
            Function to logout refresh token and blacklist the token
            args:
                token -- refresh token
        """
        blacklist_token = BlacklistToken(token=token)
        try:
            db.session.add(blacklist_token)
            db.session.commit()
        except IntegrityError as error:
            raise UnprocessableEntity("REVOKE_FAILED", "Revoke Refresh Token \
                                      failed")
        #end try
        return no_content()
    #end def
#end class
