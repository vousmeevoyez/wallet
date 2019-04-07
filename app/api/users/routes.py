""" 
    User Routes
    _______________
    this is module that handle rquest from url and then forward it to services
"""
from flask_restplus     import Resource
# db
from app.api      import db
# namespace
from app.api.users import api
# serializer
from app.api.serializer     import UserSchema
from app.api.serializer     import BankAccountSchema
# request schema
from app.api.request_schema import BankAccountRequestSchema
from app.api.request_schema import UserRequestSchema
from app.api.request_schema import UserUpdateRequestSchema
# decorator
from app.api.auth.decorator import token_required
from app.api.auth.decorator import admin_required
# services
from app.api.users.modules.bank_account_services import BankAccountServices
from app.api.users.modules.user_services import UserServices
#exceptions
from app.api.error.http import *
from marshmallow import ValidationError
# config
from app.config import config

class BaseRoutes(Resource):
    """ base class """
    error_response = config.Config.ERROR_CONFIG

@api.route("/")
class UserRoutes(BaseRoutes):
    """
        Users
        /users
    """
    @admin_required
    def post(self):
        """ Endpoint for creating user """
        request_data = UserRequestSchema.parser.parse_args(strict=True)

        # request data validator
        try:
            user = UserSchema(strict=True).load(request_data)
        except ValidationError as error:
            raise BadRequest(self.error_response["INVALID_PARAMETER"]["TITLE"],
                             self.error_response["INVALID_PARAMETER"]["MESSAGE"],
                             error.messages)

        response = UserServices().add(user.data, request_data["password"],
                                      request_data["pin"])
        return response
    #end def

    @admin_required
    def get(self):
        """ Endpoint for returning all stored user """
        response = UserServices().show(1)
        return response
#end class

@api.route("/<string:user_id>")
class UserInfoRoutes(BaseRoutes):
    """
        Users
        /users/<user_id>
    """
    @token_required
    def get(self, user_id):
        """ Endpoint for getting single user information """
        response = UserServices(user_id).info()
        return response

    @token_required
    def put(self, user_id):
        """ Endpoint for updating user information"""
        request_data = UserUpdateRequestSchema.parser.parse_args(strict=True)
        try:
            excluded = "username", "pin", "role"
            data = UserSchema(strict=True).validate(request_data,
                                                    partial=(excluded))
        except ValidationError as error:
            raise BadRequest(self.error_response["INVALID_PARAMETER"]["TITLE"],
                             self.error_response["INVALID_PARAMETER"]["MESSAGE"],
                             error.messages)

        response = UserServices(user_id).update(request_data)
        return response

    @token_required
    def delete(self, user_id):
        """ Endpoint for removing user """
        response = UserServices(user_id).remove()
        return response
#end class


@api.route("/<string:user_id>/bank_account/")
class UserBankAccountRoutes(BaseRoutes):
    """
        User Bank Accounts
        /users/<user_id>/bank_account/
    """
    @token_required
    def post(self, user_id):
        """ Endpoint for adding user bank account """
        request_data = BankAccountRequestSchema.parser.parse_args(strict=True)

        try:
            bank_account = BankAccountSchema(strict=True).load(request_data)
        except ValidationError as error:
            raise BadRequest(self.error_response["INVALID_PARAMETER"]["TITLE"],
                             self.error_response["INVALID_PARAMETER"]["MESSAGE"],
                             error.messages)
        #end try
        response = BankAccountServices(user_id, request_data["bank_code"]).add(bank_account.data)
        return response
    #end def

    @token_required
    def get(self, user_id):
        """ Endpoint for getting all user bank account """
        response = BankAccountServices(user_id).show()
        return response
    #end def
#end class

@api.route("/<string:user_id>/bank_account/<string:user_bank_account_id>")
class UserBankAccountDetailsRoutes(BaseRoutes):
    """
        User Bank Accounts 
        /users/<user_id>/bank_account/<bank_account_id>
    """
    @token_required
    def delete(self, user_id, user_bank_account_id):
        """ Endpoint for removing user bank account """
        response = BankAccountServices(user_id, None,
                                       user_bank_account_id).remove()
        return response
    #end def

    @token_required
    def put(self, user_id, user_bank_account_id):
        """ Endpoint for updating user bank account """
        request_data = BankAccountRequestSchema.parser.parse_args(strict=True)

        errors = BankAccountSchema().validate(request_data)
        if errors:
            raise BadRequest(ERROR_CONFIG["INVALID_PARAMETER"]["TITLE"],
                             ERROR_CONFIG["INVALID_PARAMETER"]["MESSAGE"],
                             errors)
        #end if
        response = BankAccountServices(user_id, request_data["bank_code"],
                                       user_bank_account_id).update(request_data)
        return response
    #end def
#end class
