import traceback
from datetime import datetime, timedelta

from flask          import request, jsonify
from sqlalchemy     import exists
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from marshmallow    import ValidationError

from app.api            import db
from app.api.wallet     import helper
from app.api.models     import User, Role
from app.api.serializer import UserSchema, WalletSchema, VirtualAccountSchema
from app.api.errors     import bad_request, internal_error, request_not_found
from app.api.config     import config

RESPONSE_MSG = config.Config.RESPONSE_MSG

class UserController:

    def __init__(self):
        pass
    #end def

    def user_register(self, params):
        response = {}

        # CREATE TRANSACTION SESSION
        try:
            session = db.session(autocommit=True)
            session.begin(subtransactions=True)
        except InvalidRequestError:
            db.session.commit()
            session = db.session()

        try:
            # fetch user role first
            role = Role.query.filter_by(description=params["role"]).first()

            # create object
            user = User(
                username=params["username"],
                name=params["name"],
                phone_ext=params["phone_ext"],
                phone_number=params["phone_number"],
                email=params["email"],
                role_id=role.id,
            )

            user.set_password(params["password"])
            session.add(user)
            session.flush()

            params["user_id"] = user.id
            # build msisdn here
            msisdn = "0" + params["phone_number"]
            params["msisdn"] = msisdn

            wallet_response = helper.WalletHelper().generate_wallet(params, session)

            if wallet_response["status"] != "SUCCESS":
                session.rollback()
                return internal_error(wallet_response["data"])
            #end if

            session.commit()

        except IntegrityError as err:
            print(err)
            session.rollback()
            return internal_error(RESPONSE_MSG["FAILED"]["ERROR_ADDING_RECORD"])
        #end try

        wallet_id = wallet_response["data"]["wallet_id"]

        response["data"] = {
            "user_id"   : user.id,
            "wallet_id" : wallet_id
        }
        response["message"] = RESPONSE_MSG["SUCCESS"]["CREATE_USER"]

        return response
    #end def

    def user_list(self, page):
        response = {}
        try:
            users = User.query.all()
            response["data"] = UserSchema(many=True).dump(users).data
        except IntegrityError as e:
            print(e)
            return bad_request(RESPONSE_MSG["FAILED"]["UNKNOWN_ERROR"])
        except ValidationError as e:
            print(e)
            return bad_request(RESPONSE_MSG["FAILED"]["UNKNOWN_ERROR"])
        except Exception as e:
            print(traceback.format_exc())
            print(str(e))
            return internal_error()

        return response
    #end def

    def user_info(self, params):
        response = {}

        try:
            user_id = params["user_id"]

            user = User.query.filter_by(id=user_id).first()
            if user == None:
                return request_not_found(RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])
            #end if

            user_information   = UserSchema().dump(user).data
            wallet_information = WalletSchema(many=True).dump(user.wallets).data

            response["data"] = {
                "user_information"   : user_information,
                "wallet_information" : wallet_information
            }

        except IntegrityError as e:
            print(e)
            return bad_request(RESPONSE_MSG["FAILED"]["UNKNOWN_ERROR"])
        except ValidationError as e:
            print(e)
            return bad_request(RESPONSE_MSG["FAILED"]["UNKNOWN_ERROR"])
        except Exception as e:
            print(traceback.format_exc())
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

        try:
            # parse request data 
            user_id = params["user_id"]

            user = User.query.filter_by(id=user_id).first()
            if user == None:
                return request_not_found(RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])
            #end if

            db.session.delete(user)
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            print(traceback.format_exc())
            print(str(e))
            return internal_error()

        response["message"] = RESPONSE_MSG["SUCCESS"]["REMOVE_USER"]
        return response
    #end def
#end class
