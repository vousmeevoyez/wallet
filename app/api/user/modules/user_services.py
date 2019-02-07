"""
    User Services
    _______________
    this is module that serve request from user routes
"""
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import InvalidRequestError

from app.api  import db

from app.api.models import Role
from app.api.models import User
from app.api.models import Wallet
from app.api.models import VirtualAccount

from app.api.serializer import UserSchema
from app.api.serializer import WalletSchema

from app.api.wallet.modules.wallet_services import WalletServices
from app.api.wallet.modules.va_services import VirtualAccountServices

# http response
from app.api.http_response import created
from app.api.http_response import no_content

# exceptions
from app.api.exception.user import UserNotFoundError
from app.api.exception.user import UserDuplicateError
from app.api.exception.user import OldRecordError

from app.api.exception.wallet import DuplicateWalletError
from app.api.exception.virtual_account import AlreadyExistVAError
# configuration
from app.config import config

STATUS_CONFIG = config.Config.STATUS_CONFIG

class UserServices:
    """ User Services Class"""
    def __init__(self, user_id):
        user = User.query.filter_by(id=user_id, status=STATUS_CONFIG["ACTIVE"]).first()
        if user is None:
            raise UserNotFoundError
        #end if
        self.user = user
    #end def

    @staticmethod
    def add(user, password, pin):
        """
            add new user
            create wallet
            create virtual account
        """
        try:
            user.set_password(password)
            db.session.add(user)
            db.session.flush()
        except IntegrityError as error:
            #print(err.orig)
            db.session.rollback()
            raise UserDuplicateError
        #end try

        # create wallet here
        try:
            wallet = Wallet()
            result = WalletServices.add(wallet, user.id, pin)
        except DuplicateWalletError as error:
            #raise CommitError(error.msg, None, error.title, None)
            pass

        wallet_id = result[0]["data"]["wallet_id"]

        # create virtual account here
        try:
            virtual_account = VirtualAccount(name=user.name)
            va_payload = {
                "bank_name" : "BNI",
                "type" : "CREDIT",
                "wallet_id" : wallet_id
            }
            result = VirtualAccountServices.add(virtual_account, va_payload)
        except AlreadyExistVAError as error:
            #raise CommitError(error.msg, None, error.title, None)
            pass

        virtual_account = result[0]["data"]["virtual_account_id"]

        response = {
            "user_id"   : user.id,
            "wallet_id" : wallet_id
        }
        return created(response)
    #end def

    @staticmethod
    def show(page):
        """ show all stored user for admin"""
        users = User.query.filter_by(status=STATUS_CONFIG["ACTIVE"]).all()
        response = UserSchema(many=True).dump(users).data
        return response
    #end def

    def info(self):
        """ return single user information"""

        user_information = UserSchema().dump(self.user).data
        wallet_information = WalletSchema(many=True).dump(self.user.wallets).data

        response = {
            "user_information"   : user_information,
            "wallet_information" : wallet_information
        }
        return response
    #end def

    def update(self, params):
        """ update user information """
        self.user.name = params["name"]
        self.user.phone_ext = params["phone_ext"]

        # checking each fields and make sure its not the same as the old one
        # and must be unique
        error = []
        phone_number = params["phone_number"]
        if self.user.phone_number == phone_number:
            error.append({
                "phone_number" : [
                    "Phone number can't be the same with the old one"
                ]
            })

        email = params["email"]
        if self.user.email == email:
            error.append({
                "email" : [
                    "email can't be the same with the old one"
                ]
            })

        if error != []:
            raise OldRecordError(error)

        self.user.set_password(params["password"])
        self.user.email = email
        self.user.phone_number = phone_number

        db.session.commit()
        return no_content()
    #end def

    def remove(self):
        """ remove user, just deactivate their account """
        try:
            self.user.status = STATUS_CONFIG["DEACTIVE"]
            db.session.commit()
        except IntegrityError as error:
            #print(err.orig)
            db.session.rollback()
        #end try
        return no_content()
    #end def
#end class
