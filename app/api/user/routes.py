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

from app.api.http_response import internal_error
from app.api.http_response import bad_request
from app.api.http_response import request_not_found

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

        # request data validator
        errors = UserSchema().validate(request_data)
        if errors:
            return bad_request(errors)
        #end if

        response = UserServices().add(request_data)
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

        errors = BankAccountSchema().validate(request_data)
        if errors:
            return bad_request(errors)
        #end if

        request_data["user_id"] = user_id

        response = BankAccountServices().add(request_data)
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

        errors = BankAccountSchema().validate(request_data)
        if errors:
            return bad_request(errors)
        #end if

        request_data["user_id"] = user_id
        request_data["user_bank_account_id"] = user_bank_account_id

        response = BankAccountServices().update(request_data)
        return response
    #end def
#end class
