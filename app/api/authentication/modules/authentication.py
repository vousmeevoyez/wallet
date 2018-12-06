import jwt
import traceback

from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError, InvalidRequestError

from app.api            import db
from app.api.models     import User, BlacklistToken
from app.api.serializer import UserSchema, WalletSchema, VirtualAccountSchema
from app.api.errors     import bad_request, internal_error, request_not_found
from app.api.config     import config

RESPONSE_MSG = config.Config.RESPONSE_MSG

class AuthController:

    def __init__(self):
        pass
    #end def

    def _create_access_token(self, user):
        token = User.encode_token("ACCESS", user.id, user.role.description)
        return token.decode()
    #end def

    def _create_refresh_token(self, user):
        token = User.encode_token("REFRESH", user.id, user.role.description)
        return token.decode()
    #end def

    @staticmethod
    def current_login_user(token):
        response = {
            "status" : "SUCCESS"
        }

        payload = User.decode_token(token)

        if not isinstance(payload, dict):
            response["status"] = "FAILED"
            response["data"  ] = payload # append the error here
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
        response = {}

        try:
            username = params["username"]
            password = params["password"]

            user = User.query.filter_by(username=username).first()
            if user == None:
                return request_not_found(RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])
            #end if

            if user.check_password(password) != True :
                return bad_request(RESPONSE_MSG["FAILED"]["INCORRECT_LOGIN"])
            #end if

            # generate token here
            access_token = self._create_access_token(user)
            refresh_token= self._create_refresh_token(user)

        except Exception as e:
            print(traceback.format_exc())
            print(str(e))
            return internal_error()
        #end try

        response["data"] = {
            "access_token" : access_token,
            "refresh_token": refresh_token
        }

        response["message"] = RESPONSE_MSG["SUCCESS"]["ACCESS_AUTH"]
        return response
    #end def

    def refresh_token(self, current_user):
        response = {}

        try:
            user = User.query.filter_by(id=current_user).first()
            if user == None:
                return request_not_found(RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])
            #end if

            access_token = self._create_access_token(user)

        except Exception as e:
            print(traceback.format_exc())
            print(str(e))
            return internal_error()
        #end try

        response["data"] = {
            "access_token" : access_token,
        }

        response["message"] = RESPONSE_MSG["SUCCESS"]["REFRESH_AUTH"]
        return response
    #end def

    def logout_access_token(self, token):
        response = {}

        try:
            # decode the token first
            resp = User.decode_token(token)

            if not isinstance(resp, dict):
                return bad_request(resp)
            #end if

            blacklist_token = BlacklistToken(token=token)

            db.session.add(blacklist_token)
            db.session.commit()

        except Exception as e:
            print(traceback.format_exc())
            print(str(e))
            return internal_error()
        #end try

        response["message"] = RESPONSE_MSG["SUCCESS"]["LOGOUT_AUTH"]
        return response
    #end def

    def logout_refresh_token(self, token):
        response = {}

        try:
            # decode the token first
            resp = User.decode_token(token)

            if not isinstance(resp, dict):
                return bad_request(resp)
            #end if

            blacklist_token = BlacklistToken(token=token)

            db.session.add(blacklist_token)
            db.session.commit()

        except Exception as e:
            print(traceback.format_exc())
            print(str(e))
            return internal_error()
        #end try

        response["message"] = RESPONSE_MSG["SUCCESS"]["LOGOUT_REFRESH"]
        return response
    #end def
#end class
