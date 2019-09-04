"""
    User Routes
    _______________
"""
#pylint: disable=no-name-in-module
#pylint: disable=import-error
#pylint: disable=no-self-use

from app.api.core import Routes
from app.api.users import api
# serializer
from app.api.serializer import UserSchema, BankAccountSchema
# request schema
from app.api.request_schema import (
    BankAccountRequestSchema,
    UserRequestSchema,
    UserUpdateRequestSchema
)
# decorator
from app.api.auth.decorator import token_required, admin_required
# services
from app.api.users.modules.bank_account_services import BankAccountServices
from app.api.users.modules.user_services import UserServices

@api.route("/")
class UserRoutes(Routes):
    """
        Users
        /users
    """
    __schema__ = UserRequestSchema
    __serializer__ = UserSchema(strict=True)

    @admin_required
    def post(self):
        """ Endpoint for creating user """
        request_data = self.payload()
        user = self.serialize(request_data, load=True)

        response = UserServices().add(
            user, request_data["password"], request_data["pin"], request_data["label"]
        )
        return response
    #end def

    @admin_required
    def get(self):
        """ Endpoint for returning all stored user """
        response = UserServices().show(1)
        return response
#end class

@api.route("/<string:user_id>")
class UserInfoRoutes(Routes):
    """
        Users
        /users/<user_id>
    """

    __schema__ = UserUpdateRequestSchema
    __serializer__ = UserSchema(exclude=("username", "pin", "role", "label"))

    @token_required
    def get(self, user_id):
        """ Endpoint for getting single user information """
        response = UserServices(user_id).info()
        return response

    @token_required
    def put(self, user_id):
        """ Endpoint for updating user information"""
        request_data = self.serialize(self.payload())

        response = UserServices(user_id).update(request_data)
        return response

    @token_required
    def delete(self, user_id):
        """ Endpoint for removing user """
        response = UserServices(user_id).remove()
        return response
#end class


@api.route("/<string:user_id>/bank_account/")
class UserBankAccountRoutes(Routes):
    """
        User Bank Accounts
        /users/<user_id>/bank_account/
    """

    __schema__ = BankAccountRequestSchema
    __serializer__ = BankAccountSchema(strict=True)

    @token_required
    def post(self, user_id):
        """ Endpoint for adding user bank account """
        request_data = self.payload()
        bank_account = self.serialize(request_data, load=True)

        response = BankAccountServices(user_id, request_data["bank_code"]).add(bank_account)
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
class UserBankAccountDetailsRoutes(Routes):
    """
        User Bank Accounts
        /users/<user_id>/bank_account/<bank_account_id>
    """

    __schema__ = BankAccountRequestSchema
    __serializer__ = BankAccountSchema(strict=True)

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
        request_data = self.serialize(self.payload())

        response = BankAccountServices(user_id, request_data["bank_code"],
                                       user_bank_account_id).update(request_data)
        return response
    #end def
#end class
