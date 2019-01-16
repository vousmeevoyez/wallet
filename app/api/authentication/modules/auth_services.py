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
# http errors
from app.api.errors import bad_request
from app.api.errors import internal_error
from app.api.errors import request_not_found
# configuration
from app.api.config import config

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

        response = {
            "status" : "SUCCESS"
        }

        payload = User.decode_token(token)

        if not isinstance(payload, dict):
            response["status"] = "FAILED"
            response["data"] = payload # append the error here
            return response
        #end if

        # fetch user information
        response["data"] = {
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
        response = {}

        username = params["username"]
        password = params["password"]

        user = User.query.filter_by(username=username).first()
        if user is None:
            return request_not_found(RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])
        #end if

        if user.check_password(password) is not True:
            return bad_request(RESPONSE_MSG["FAILED"]["INCORRECT_LOGIN"])
        #end if

        # generate token here
        access_token = self._create_access_token(user)
        refresh_token = self._create_refresh_token(user)

        response["data"] = {
            "access_token" : access_token,
            "refresh_token": refresh_token
        }

        response["message"] = RESPONSE_MSG["SUCCESS"]["ACCESS_AUTH"]
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
            return request_not_found(RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])
        #end if

        access_token = self._create_access_token(user)

        response["data"] = {
            "access_token" : access_token,
        }

        response["message"] = RESPONSE_MSG["SUCCESS"]["REFRESH_AUTH"]
        return response
    #end def

    def logout_access_token(self, token):
        """
            Function to logout access token and blacklist the token
            args:
                token -- access token
        """
        response = {}

        # decode the token first
        resp = User.decode_token(token)

        if not isinstance(resp, dict):
            return bad_request(resp)
        #end if

        blacklist_token = BlacklistToken(token=token)

        try:
            db.session.add(blacklist_token)
            db.session.commit()
        except IntegrityError as error:
            print(str(error))
            return internal_error()
        #end try

        response["message"] = RESPONSE_MSG["SUCCESS"]["LOGOUT_AUTH"]
        return response
    #end def

    def logout_refresh_token(self, token):
        """
            Function to logout refresh token and blacklist the token
            args:
                token -- refresh token
        """
        response = {}

        # decode the token first
        resp = User.decode_token(token)

        if not isinstance(resp, dict):
            return bad_request(resp)
        #end if

        blacklist_token = BlacklistToken(token=token)

        try:
            db.session.add(blacklist_token)
            db.session.commit()
        except IntegrityError as error:
            print(str(error))
            return internal_error()
        #end try

        response["message"] = RESPONSE_MSG["SUCCESS"]["LOGOUT_REFRESH"]
        return response
    #end def
#end class
