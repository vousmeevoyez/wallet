""" 
    User Routes
    _______________
    this is module that handle rquest from url and then forward it to services
"""
from flask              import request
from flask_restplus     import Resource

from app.api                import db
from app.api.user           import api
from app.api.serializer     import UserSchema, BankAccountSchema
from app.api.request_schema import UserRequestSchema, BankAccountRequestSchema

from app.api.authentication.decorator import token_required, admin_required

from app.api.user.modules.bank_account_services import BankAccountServices
from app.api.user.modules.user_services import UserServices

from app.api.errors import bad_request, internal_error, request_not_found

user_request_schema = UserRequestSchema.parser
user_bank_account_request_schema = BankAccountRequestSchema.parser

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
        request_data = user_request_schema.parse_args(strict=True)
        data = {
            "username"    : request_data["username"],
            "name"        : request_data["name"],
            "phone_ext"   : request_data["phone_ext"],
            "phone_number": request_data["phone_number"],
            "email"       : request_data["email"],
            "password"    : request_data["password"],
            "pin"         : request_data["pin"],
            "role"        : request_data["role"],
        }

        # request data validator
        errors = UserSchema().validate(data)
        if errors:
            return bad_request(errors)
        #end if

        response = UserServices().add(data)
        return response
    #end def

    @admin_required
    def get(self):
        """
            handle GET method from
            api/v1/user/
            return all stored user
        """
        response = UserServices().show(1)
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
        response = UserServices().info({"user_id" : user_id})
        return response
    #end def
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
        request_data = user_bank_account_request_schema.parse_args(strict=True)
        data = {
            "account_no" : request_data["account_no"],
            "label"      : request_data["label"],
            "name"       : request_data["name"],
            "bank_code"  : request_data["bank_code"],
        }

        errors = BankAccountSchema().validate(data)
        if errors:
            return bad_request(errors)
        #end if

        data["user_id"] = user_id

        response = BankAccountServices().add(data)
        return response
    #end def

    @token_required
    def get(self, user_id):
        """
            handle GET method from
            api/v1/user/<user_id>/bank_account/
            get all user bank account information
        """
        response = BankAccountServices().show({"user_id" : user_id})
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
        response = BankAccountServices().remove({
            "user_id" : user_id,
            "user_bank_account_id" : user_bank_account_id
        })
        return response
    #end def

    @token_required
    def put(self, user_id, user_bank_account_id):
        """
            Handle Put Method
            api/v1/user/<user_id>/bank_account/<user_bank_account_id>
        """
        request_data = user_bank_account_request_schema.parse_args(strict=True)
        data = {
            "account_no" : request_data["account_no"],
            "label"      : request_data["label"],
            "name"       : request_data["name"],
            "bank_code"  : request_data["bank_code"],
        }

        errors = BankAccountSchema().validate(data)
        if errors:
            return bad_request(errors)
        #end if

        data["user_id"] = user_id
        data["user_bank_account_id"] = user_bank_account_id

        response = BankAccountServices().update(data)
        return response
    #end def
#end class
