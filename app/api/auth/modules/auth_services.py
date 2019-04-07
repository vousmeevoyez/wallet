"""
    Auth Services
    _________________
    This services module to handle all incoming authenticaion
"""

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
# sqlalchemy exceptions
from sqlalchemy.exc import IntegrityError
# http error
from app.api.error.http import *
# utility
from app.api.utility.utils import validate_uuid
# http response
from app.api.http_response import *
# configuration
from app.config import config

class AuthServices:
    """ Authentication Services Class"""

    error_response  = config.Config.ERROR_CONFIG
    status_config = config.Config.STATUS_CONFIG

    @staticmethod
    def _create_token(user, token_type):
        """ get user object and then create access token"""
        token = User.encode_token(token_type, user.id)
        return token.decode()
    #end def

    def current_login_user(self, token):
        """
            function to check who is currently login by decode their token
            used in decorator
            args:
                token -- jwt token
        """
        try:
            payload = User.decode_token(token)
        except RevokedTokenError:
            raise Unauthorized(self.error_response["REVOKED_TOKEN"]["TITLE"],
                               self.error_response["REVOKED_TOKEN"]["MESSAGE"])
        except SignatureExpiredError as error:
            #print(error)
            raise Unauthorized(self.error_response["SIGNATURE_EXPIRED"]["TITLE"],
                               self.error_response["SIGNATURE_EXPIRED"]["MESSAGE"])
        except InvalidTokenError as error:
            #print(error)
            raise Unauthorized(self.error_response["INVALID_TOKEN"]["TITLE"],
                               self.error_response["INVALID_TOKEN"]["MESSAGE"])
        except EmptyPayloadError:
            raise Unauthorized(self.error_response["EMPTY_PAYLOAD"]["TITLE"],
                               self.error_response["EMPTY_PAYLOAD"]["MESSAGE"])

        # fetch user information
        user = User.query.filter_by(id=validate_uuid(payload["sub"]), 
                                    status=self.status_config["ACTIVE"]).first()
        if user is None:
            raise RequestNotFound(self.error_response["USER_NOT_FOUND"]["TITLE"],
                                  self.error_response["USER_NOT_FOUND"]["MESSAGE"])

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
                params -- dict (username, password)
        """
        username = params["username"]
        password = params["password"]

        user = User.query.filter_by(username=username).first()
        if user is None:
            raise RequestNotFound(self.error_response["USER_NOT_FOUND"]["TITLE"],
                                  self.error_response["USER_NOT_FOUND"]["MESSAGE"])
        #end if

        if user.check_password(password) is not True:
            raise Unauthorized(self.error_response["INVALID_CREDENTIALS"]["TITLE"],
                               self.error_response["INVALID_CREDENTIALS"]["MESSAGE"])
        #end if

        # generate token here
        access_token = self._create_token(user, "ACCESS")
        refresh_token = self._create_token(user, "REFRESH")

        response = {
            "access_token" : access_token,
            "refresh_token": refresh_token
        }
        return ok(response)
    #end def

    def refresh_token(self, current_user):
        """
            Function to create refresh token
            args:
                current_user -- user object
        """
        access_token = self._create_token(current_user, "REFRESH")
        response = {
            "access_token" : access_token,
        }
        return ok(response)
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
