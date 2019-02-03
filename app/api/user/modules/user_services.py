"""
    User Services
    _______________
    this is module that serve request from user routes
"""
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import InvalidRequestError

from app.api  import db
from app.api.wallet import helper

from app.api.models import Role
from app.api.models import User

from app.api.serializer import UserSchema
from app.api.serializer import WalletSchema
# http response
from app.api.http_response import created
from app.api.http_response import no_content
from app.api.http_response import request_not_found
from app.api.http_response import unprocessable_entity

# configuration
from app.config import config

ERROR = config.Config.ERROR_HEADER
STATUS_CONFIG = config.Config.STATUS_CONFIG

class UserServices:
    """ User Services Class"""

    def add(self, params):
        """
            add new user
        """
        # CREATE TRANSACTION SESSION
        session = db.session()
        session.begin(nested=True)

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
            #print(err.orig)
            session.rollback()
            return unprocessable_entity(ERROR["DUPLICATE_USER"])
        #end try

        params["user_id"] = user.id
        # build msisdn here
        msisdn = "0" + params["phone_number"]
        params["msisdn"] = msisdn

        # create wallet
        # create va

        session.commit()

        response = {
            "user_id"   : user.id,
            "wallet_id" : None
        }
        return created(response)
    #end def

    def show(self, page):
        """ show all stored user for admin"""
        users = User.query.all()
        response = UserSchema(many=True).dump(users).data
        return response
    #end def

    def info(self, params):
        """ return single user information"""
        user_id = params["user_id"]

        user = User.query.filter_by(id=user_id, status=STATUS_CONFIG["ACTIVE"]).first()
        if user is None:
            return request_not_found()
        #end if

        user_information = UserSchema().dump(user).data
        wallet_information = WalletSchema(many=True).dump(user.wallets).data

        response = {
            "user_information"   : user_information,
            "wallet_information" : wallet_information
        }
        return response
    #end def

    def remove(self, params):
        """ remove user, just deactivate their account """

        # parse request data
        user_id = params["user_id"]

        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return request_not_found()
        #end if

        try:
            user.status = STATUS_CONFIG["DEACTIVE"]
            db.session.commit()
        except IntegrityError as error:
            #print(err.orig)
            db.session.rollback()
            return unprocessable_entity("Failed removing user")
        #end try
        return no_content()
    #end def
#end class
