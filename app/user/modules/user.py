import traceback
from datetime import datetime, timedelta

from flask          import request, jsonify
from sqlalchemy.exc import IntegrityError, InvalidRequestError

from app            import db
from app.user       import bp
from app.wallet     import helper
from app.models     import User
from app.serializer import UserSchema, WalletSchema, VirtualAccountSchema
from app.errors     import bad_request, internal_error, request_not_found
from app.config     import config

ACCESS_KEY_CONFIG = config.Config.ACCESS_KEY_CONFIG
VA_TYPE           = config.Config.VA_TYPE_CONFIG
TRANSACTION_NOTES = config.Config.TRANSACTION_NOTES
RESPONSE_MSG      = config.Config.RESPONSE_MSG

class UserController:

    def __init__(self):
        pass
    #end def

    def user_register(self, params):
        response = {
            "status_code"    : 0,
            "status_message" : "SUCCESS",
            "data"           : "NONE"
        }

        try:
            # CREATE TRANSACTION SESSION
            session = db.session(autocommit=True)
            session.begin(subtransactions=True)

            try:
                # create object
                user = User(
                    username=params["username"],
                    name=params["name"],
                    msisdn=params["msisdn"],
                    email=params["email"],
                    role=params["role"],
                )

                user.set_password(params["password"])
                session.add(user)
                session.commit()

                params["user_id"] = user.id
                wallet_response = helper.WalletHelper().generate_wallet(params, session)

                if wallet_response["status"] != "SUCCESS":
                    session.delete(user)
                    session.rollback()
                    return bad_request(wallet_response["data"])
                #end if

            except IntegrityError as err:
                session.rollback()
                return bad_request(RESPONSE_MSG["ERROR_ADDING_RECORD"])

        except Exception as e:
            print(traceback.format_exc())
            print(str(e))
            return internal_error()
        #end try

        wallet_id = wallet_response["data"]["wallet_id"]

        response["data"] = {
            "user_id"   : user.id,
            "wallet_id" : wallet_id
        }
        response["status_message"] = RESPONSE_MSG["SUCCESS_CREATE_USER"]

        return response
    #end def

    def user_list(self, page):
        response = {
            "status_code"    : 0,
            "status_message" : "SUCCESS",
            "data"           : "NONE"
        }

        try:
            users = User.query.all()
            response["data"] = UserSchema(many=True).dump(users).data
        except Exception as e:
            print(str(e))
            return internal_error()
        #end try

        return response
    #end def

    def user_info(self, params):
        response = {
            "status_code"    : 0,
            "status_message" : "SUCCESS",
            "data"           : "NONE"
        }

        try:
            user_id = params["user_id"]

            user = User.query.filter_by(id=user_id).first()
            if user == None:
                return request_not_found()

            user_information   = UserSchema().dump(user).data
            wallet_information = WalletSchema(many=True).dump(user.wallets).data

            response["data"] = {
                "user_information"   : user_information,
                "wallet_information" : wallet_information
            }

        except Exception as e:
            print(str(e))
            return internal_error()

        return response
    #end def

    def remove_user(self, params):
        response = {
            "status_code"    : 0,
            "status_message" : "SUCCESS",
            "data"           : "NONE"
        }

        db.session.begin()

        try:
            # parse request data 
            user_id = params["user_id"]

            user = User.query.filter_by(id=user_id).first()
            if user == None:
                return request_not_found()

            db.session.delete(user)
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            print(traceback.format_exc())
            print(str(e))
            return internal_error()

        response["data"] = RESPONSE_MSG["USER_REMOVED"]

        return response
    #end def

    def update_user(self, params):
        response = {
            "status_code"    : 0,
            "status_message" : "SUCCESS",
            "data"           : "NONE"
        }

        db.session.begin()

        try:
            # parse request data 
            user_id   = params["user_id" ]
            name      = params["name"    ]
            msisdn    = params["msisdn"  ]
            email     = params["email"   ]

            user = User.query.filter_by(id=user_id).first()
            if user == None:
                return request_not_found()

            user.name   = name
            user.msisdn = msisdn
            user.email  = email

            db.session.commit()

        except Exception as e:
            db.session.rollback()
            print(traceback.format_exc())
            print(str(e))
            return internal_error()

        response["data"] = RESPONSE_MSG["USER_UPDATED"]

        return response
    #end def

#end class
