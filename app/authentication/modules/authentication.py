import traceback
from datetime import datetime, timedelta

from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)
from flask          import request, jsonify
from sqlalchemy.exc import IntegrityError, InvalidRequestError

from app                import db, jwt
from app.authentication import bp
from app.models         import User, BlacklistToken
from app.serializer     import UserSchema, WalletSchema, VirtualAccountSchema
from app.errors         import bad_request, internal_error, request_not_found
from app.config         import config

RESPONSE_MSG = config.Config.RESPONSE_MSG

class AuthController:

    def __init__(self):
        pass
    #end def

    def create_token(self, params):
        response = {
            "status_code"    : 0,
            "status_message" : "SUCCESS",
            "data"           : "NONE"
        }

        try:

            username = params["username"]
            password = params["password"]

            user = User.query.filter_by(username=username).first()
            if user == None:
                return request_not_found()
            #end if

            if user.check_password(password) != True :
                return bad_request(RESPONSE_MSG["INCORRECT_LOGIN"])
            #end if

            # generate token here
            access_token = create_access_token(identity=user)
            refresh_token= create_refresh_token(identity=user)

        except Exception as e:
            print(traceback.format_exc())
            print(str(e))
            return internal_error()
        #end try

        response["data"] = {
            "access_token" : access_token,
            "refresh_token": refresh_token
        }

        response["status_message"] = RESPONSE_MSG["SUCCESS_AUTH"]

        return response
    #end def

    def refresh_token(self, current_user):
        response = {
            "status_code"    : 0,
            "status_message" : "SUCCESS",
            "data"           : "NONE"
        }

        try:

            access_token = create_access_token(identity=current_user)

        except Exception as e:
            print(traceback.format_exc())
            print(str(e))
            return internal_error()
        #end try

        response["data"] = {
            "access_token" : access_token,
        }

        response["status_message"] = RESPONSE_MSG["REFRESH_AUTH"]

        return response
    #end def

    def logout_access_token(self, token):
        response = {
            "status_code"    : 0,
            "status_message" : "SUCCESS",
            "data"           : "NONE"
        }

        try:

            blacklist_token = BlacklistToken(token=token)

            db.session.add(blacklist_token)
            db.session.commit()

        except Exception as e:
            print(traceback.format_exc())
            print(str(e))
            return internal_error()
        #end try

        response["status_message"] = RESPONSE_MSG["LOGOUT_AUTH"]

        return response
    #end def

    def logout_refresh_token(self, token):
        response = {
            "status_code"    : 0,
            "status_message" : "SUCCESS",
            "data"           : "NONE"
        }

        try:

            blacklist_token = BlacklistToken(token=token)

            db.session.add(blacklist_token)
            db.session.commit()

        except Exception as e:
            print(traceback.format_exc())
            print(str(e))
            return internal_error()
        #end try

        response["status_message"] = RESPONSE_MSG["LOGOUT_REFRESH"]

        return response
    #end def
#end class
