""" 
    User Routes
    _______________
    this is module that handle rquest from url and then forward it to services
"""
from flask_restplus     import Resource
from marshmallow import ValidationError

from app.api      import db
from app.api.user import api

# serializer
from app.api.serializer     import UserSchema
from app.api.serializer     import BankAccountSchema
# request schema
from app.api.request_schema import BankAccountRequestSchema
from app.api.request_schema import UserRequestSchema
from app.api.request_schema import UserUpdateRequestSchema

# decorator
from app.api.authentication.decorator import token_required
from app.api.authentication.decorator import admin_required
# services
from app.api.user.modules.bank_account_services import BankAccountServices
from app.api.user.modules.user_services import UserServices

#http exception
from app.api.exception.general import SerializeError
from app.api.exception.general import RecordNotFoundError
from app.api.exception.general import CommitError

from app.api.exception.user import UserDuplicateError
from app.api.exception.user import UserNotFoundError
from app.api.exception.user import OldRecordError

from app.api.exception.bank import BankNotFoundError
from app.api.exception.bank import BankAccountNotFoundError
from app.api.exception.bank import DuplicateBankAccountError

USER_REQUEST_SCHEMA = UserRequestSchema.parser
USER_UPDATE_REQUEST_SCHEMA = UserUpdateRequestSchema.parser
USER_BANK_ACC_REQUEST_SCHEMA = BankAccountRequestSchema.parser

@api.route("/")
class UserRoutes(Resource):
    """
        User Routes
        api/v1/user/
    """
    @admin_required
    def post(self):
        """
            handle POST method from
            api/v1/user/
            create user
        """
        request_data = USER_REQUEST_SCHEMA.parse_args(strict=True)

        # request data validator
        try:
            user = UserSchema(strict=True).load(request_data)
        except ValidationError as error:
            raise SerializeError(error.messages)

        try:
            response = UserServices.add(user.data, request_data["password"],
                                        request_data["pin"])
        except UserDuplicateError as error:
            raise CommitError(error.msg, error.title)
        return response
    #end def

    @admin_required
    def get(self):
        """
            handle GET method from
            api/v1/user/
            return all stored user
        """
        response = UserServices.show(1)
        return response
#end class

@api.route("/<int:user_id>")
class UserInfoRoutes(Resource):
    """
        User Info Routes
        api/v1/user/<user_id>
    """
    @token_required
    def get(self, user_id):
        """
            handle GET method from
            api/v1/user/<user_id>
            return single user information
        """
        try:
            response = UserServices(user_id).info()
        except UserNotFoundError as error:
            raise RecordNotFoundError(error.msg, error.title)
        return response

    @token_required
    def put(self, user_id):
        """
            handle PUT method from
            api/v1/user/<user_id>
            return updated user information
        """
        request_data = USER_UPDATE_REQUEST_SCHEMA.parse_args(strict=True)
        
        excluded = "username", "pin", "role"
        errors = UserSchema(strict=True).validate(request_data,
                                                  partial=(excluded))
        if errors:
            raise SerializeError(errors)

        try:
            response = UserServices(user_id).update(request_data)
        except UserNotFoundError as error:
            raise RecordNotFoundError(error.msg, error.title)
        except OldRecordError as error:
            raise CommitError(error.msg, error.title, error.details)
        return response

    @token_required
    def delete(self, user_id):
        """
            handle DELETE method from
            api/v1/user/<user_id>
            return updated user information
        """
        try:
            response = UserServices(user_id).remove()
        except UserNotFoundError as error:
            raise RecordNotFoundError(error.msg, error.title)
        return response
#end class


@api.route("/<int:user_id>/bank_account/")
class UserBankAccountRoutes(Resource):
    """
        User Bank Account Routes
        api/v1/user/<user_id>/bank_account/
    """
    @token_required
    def post(self, user_id):
        """
            handle POST method from
            api/v1/user/<user_id>/bank_account/
            create user bank account
        """
        request_data = USER_BANK_ACC_REQUEST_SCHEMA.parse_args(strict=True)

        try:
            bank_account = BankAccountSchema(strict=True).load(request_data)
        except ValidationError as error:
            raise SerializeError(error.messages)
        #end try
        try:
            response = BankAccountServices(user_id, request_data["bank_code"]).add(bank_account.data)
        except (UserNotFoundError,
                BankNotFoundError,
                BankAccountNotFoundError) as error:
            raise RecordNotFoundError(error.msg, error.title)
        except DuplicateBankAccountError as error:
            raise CommitError(error.msg, error.title)
        return response
    #end def

    @token_required
    def get(self, user_id):
        """
            handle GET method from
            api/v1/user/<user_id>/bank_account/
            get all user bank account information
        """
        response = BankAccountServices(user_id).show()
        return response
    #end def
#end class

@api.route("/<int:user_id>/bank_account/<int:user_bank_account_id>")
class UserBankAccountDetailsRoutes(Resource):
    """
        User Account Details Routes
        api/v1/user/<user_id>/bank_account/<user_bank_account_id>
    """
    @token_required
    def delete(self, user_id, user_bank_account_id):
        """
            Handle DELETE Method
            api/v1/user/<user_id>/bank_account/<user_bank_account_id>
        """
        response = BankAccountServices(user_id, None,
                                       user_bank_account_id).remove()
        return response
    #end def

    @token_required
    def put(self, user_id, user_bank_account_id):
        """
            Handle Put Method
            api/v1/user/<user_id>/bank_account/<user_bank_account_id>
        """
        request_data = USER_BANK_ACC_REQUEST_SCHEMA.parse_args(strict=True)

        errors = BankAccountSchema().validate(request_data)
        if errors:
            raise SerializeError(errors)
        #end if
        response = BankAccountServices(user_id, request_data["bank_code"], user_bank_account_id).update(request_data)
        return response
    #end def
#end class
