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

class Token:
    """ Handle everything related to Token """

    def __init__(self, token):
        self.token = token
    # end def

    @staticmethod
    def create(user, token_type):
        """
            create token
        """
        token = User.encode_token(token_type, user.id)
        return token.decode()
    #end def

    def decode(self):
        """
            decode token
        """
        try:
            payload = User.decode_token(self.token)
        except RevokedTokenError:
            return "REVOKED_TOKEN"
        except SignatureExpiredError:
            return "SIGNATURE_EXPIRED"
        except InvalidTokenError:
            return "INVALID_TOKEN"
        except EmptyPayloadError:
            return "EMPTY_PAYLOAD"
        # end try
        return payload
    # end def

    def blacklist(self):
        """
            blacklist a token
        """
        blacklist_token = BlacklistToken(token=self.token)
        try:
            db.session.add(blacklist_token)
            db.session.commit()
        except IntegrityError:
            return False
        #end try
        return True
    # end def
# end class

class AuthServices:
    """ Authentication Services Class"""

    error_response = config.Config.ERROR_CONFIG
    status_config = config.Config.STATUS_CONFIG

    def current_login_user(self, token):
        """
            function to check who is currently login by decode their token
            used in decorator
        """
        payload = Token(token).decode()
        if isinstance(payload, str):
            raise Unauthorized(self.error_response[payload]["TITLE"],
                               self.error_response[payload]["MESSAGE"])

        # fetch user information
        user = User.query.filter_by(id=validate_uuid(payload["sub"]),
                                    status=self.status_config["ACTIVE"]).first()
        if user is None:
            raise RequestNotFound(self.error_response["USER_NOT_FOUND"]["TITLE"],
                                  self.error_response["USER_NOT_FOUND"]["MESSAGE"])
        # end if

        response = {
            "token_type": payload["type"],
            "user"      : user,
        }
        return response
    #end def

    def create_token(self, params):
        """
            Function to create token
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
        access_token = Token.create(user, "ACCESS")
        refresh_token = Token.create(user, "REFRESH")

        response = {
            "access_token" : access_token,
            "refresh_token": refresh_token
        }
        return ok(response)
    #end def

    def refresh_token(self, current_user):
        """
            Function to create refresh token
        """
        access_token = Token.create(current_user, "REFRESH")
        response = {
            "access_token" : access_token,
        }
        return ok(response)
    #end def

    def logout(self, token):
        """
            Function to logout access token and blacklist the token
        """
        has_been_blacklisted = Token(token).blacklist()
        if has_been_blacklisted is False:
            raise UnprocessableEntity("REVOKE_FAILED", "Revoke Token failed")
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
