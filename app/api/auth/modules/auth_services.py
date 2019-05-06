"""
    Auth Services
    _________________
    This services module to handle all incoming authenticaion
"""
#pylint: disable=no-name-in-module
#pylint: disable=import-error
# sqlalchemy exceptions
from sqlalchemy.exc import IntegrityError

from app.api import db
# models
from app.api.models import User
from app.api.models import BlacklistToken
from app.api.models import ApiKey
# exceptions
from app.api.error.authentication import RevokedTokenError
from app.api.error.authentication import SignatureExpiredError
from app.api.error.authentication import InvalidTokenError
from app.api.error.authentication import EmptyPayloadError
# http error
from app.api.error.http import Unauthorized
from app.api.error.http import UnprocessableEntity
from app.api.error.http import RequestNotFound
# utility
from app.api.utility.utils import validate_uuid
# http response
from app.api.http_response import ok, no_content
# configuration
from app.config import config

class AuthServices:
    """ Authentication Services Class"""

    error_response = config.Config.ERROR_CONFIG
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
        except SignatureExpiredError:
            raise Unauthorized(self.error_response["SIGNATURE_EXPIRED"]["TITLE"],
                               self.error_response["SIGNATURE_EXPIRED"]["MESSAGE"])
        except InvalidTokenError:
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

    @staticmethod
    def logout_access_token(token):
        """
            Function to logout access token and blacklist the token
            args:
                token -- access token
        """
        blacklist_token = BlacklistToken(token=token)
        try:
            db.session.add(blacklist_token)
            db.session.commit()
        except IntegrityError:
            raise UnprocessableEntity("REVOKE_FAILED", "Revoke Access Token \
                                      failed")
        #end try
        return no_content()
    #end def

    @staticmethod
    def logout_refresh_token(token):
        """
            Function to logout refresh token and blacklist the token
            args:
                token -- refresh token
        """
        blacklist_token = BlacklistToken(token=token)
        try:
            db.session.add(blacklist_token)
            db.session.commit()
        except IntegrityError:
            raise UnprocessableEntity("REVOKE_FAILED", "Revoke Refresh Token \
                                      failed")
        #end try
        return no_content()
    #end def

    ################ PATCH ########################
    @staticmethod
    def check_key(api_key):
        """ look up api key in db """
        api_key = ApiKey.query.filter_by(id=validate_uuid(api_key)).first()
        if api_key is None:
            raise Unauthorized("INVALID_API_KEY", "Invalid Api Key")
        return api_key
    # end def
#end class
