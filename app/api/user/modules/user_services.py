"""
    User Services
    _______________
    this is module that serve request from user routes
"""
import traceback

from flask          import request, jsonify
from sqlalchemy     import exists
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from marshmallow    import ValidationError

from app.api            import db
from app.api.wallet     import helper
from app.api.models     import User, Role
from app.api.serializer import UserSchema
from app.api.serializer import WalletSchema
from app.api.errors     import bad_request, internal_error, request_not_found
from app.api.config     import config

RESPONSE_MSG = config.Config.RESPONSE_MSG

class UserServices:
    """ User Services Class"""

    def add(self, params):
        """
            add new user
        """
        response = {}

        # CREATE TRANSACTION SESSION
        try:
            session = db.session(autocommit=True)
            session.begin(subtransactions=True)
        except InvalidRequestError:
            db.session.commit()
            session = db.session()

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

        try:
            session.add(user)
            session.flush()
        except IntegrityError as err:
            print(err)
            session.rollback()
            return internal_error(RESPONSE_MSG["FAILED"]["ERROR_ADDING_RECORD"])
        #end try

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

        wallet_id = wallet_response["data"]["wallet_id"]

        response["data"] = {
            "user_id"   : user.id,
            "wallet_id" : wallet_id
        }
        response["message"] = RESPONSE_MSG["SUCCESS"]["CREATE_USER"]
        return response
    #end def

    def show(self, page):
        """ show all stored user"""
        response = {}

        users = User.query.all()
        response["data"] = UserSchema(many=True).dump(users).data

        return response
    #end def

    def info(self, params):
        """ return single user information"""
        response = {}

        user_id = params["user_id"]

        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return request_not_found(RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])
        #end if

        user_information   = UserSchema().dump(user).data
        wallet_information = WalletSchema(many=True).dump(user.wallets).data

        response["data"] = {
            "user_information"   : user_information,
            "wallet_information" : wallet_information
        }
        return response
    #end def

    def remove(self, params):
        """ remove user"""
        response = {}

        try:
            # parse request data 
            user_id = params["user_id"]

            user = User.query.filter_by(id=user_id).first()
            if user is None:
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
