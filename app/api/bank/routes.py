"""
    Bank routes
"""
from flask_restplus     import Resource

from app.api.bank import api
from app.api.serializer import BankSchema
from app.api.request_schema import BNIUtilityRequestSchema

from app.api.authentication.decorator import admin_required

from app.api.bank.modules.bank_services import BankServices

request_schema = BNIUtilityRequestSchema.parser

@api.route("/")
class BankRoutes(Resource):
    def get(self):
        response = BankServices().get_banks()
        return response
    #end def
#end class

@api.route("/bni/balance/<string:account_no>")
class BNIHostBalanceRoutes(Resource):
    """
        BNI Utility Function
        Check HOST Balance
    """
    @admin_required
    def get(self, account_no):
        response = BankServices().get_host_balance(account_no)
        return response
    #end def
#end class

@api.route("/bni/inquiry/<string:account_no>")
class BNIInquiryRoutes(Resource):
    """
        BNI Utility Function
        Check Account Information
    """
    @admin_required
    def get(self, account_no):
        response = BankServices().get_account_information(account_no)
        return response
    #end def
#end class

@api.route("/bni/payment/<string:ref_number>")
class BNIPaymentRoutes(Resource):
    """
        BNI Utility Function
        Check Payment Status
    """
    @admin_required
    def get(self, ref_number):
        response = BankServices().get_payment_status(ref_number)
        return response
    #end def

    @admin_required
    def delete(self, ref_number):
        request_data = request_schema.parse_args(strict=True)
        account_no = request_data["account_no"]
        amount = request_data["amount"]
        response = BankServices().void_payment(ref_number, account_no, amount)
        return response
    #end def
#end class
