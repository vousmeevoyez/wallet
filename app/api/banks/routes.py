"""
    Bank routes
    _____________
    Module that handler routes for bank
"""
#pylint: disable=no-name-in-module
#pylint: disable=no-self-use
# core
from flask_restplus import Resource
# namespace
from app.api.banks import api
# request schema
from app.api.request_schema import (
    BNIUtilityRequestSchema,
    BNIUtilityDoPaymentRequestSchema,
    BNIUtilityInterbankInquiryRequestSchema,
    BNIUtilityInterbankPaymentRequestSchema
)

# decorator
from app.api.auth.decorator import admin_required
# services
from app.api.banks.modules.bank_services import BankServices

@api.route("/")
class BankRoutes(Resource):
    """
        Banks
        /banks/
    """
    def get(self):
        """ Endpoint for getting list of bank """
        response = BankServices().get_banks()
        return response
    #end def
#end class

@api.route("/bni/balance/<string:account_no>")
class BNIHostBalanceRoutes(Resource):
    """
        Banks
        /banks/bni/balance/<account_no>
    """
    @admin_required
    def get(self, account_no):
        """ Endpoint for getting BNI account Balance """
        response = BankServices().get_host_balance(account_no)
        return response
    #end def
#end class

@api.route("/bni/inquiry/<string:account_no>")
class BNIInquiryRoutes(Resource):
    """
        Banks
        /banks/bni/inquiry/<account_no>
    """
    @admin_required
    def get(self, account_no):
        """ Endpoint for getting BNI inquiry account """
        response = BankServices().get_account_information(account_no)
        return response
    #end def
#end class

@api.route("/bni/payment/<string:ref_number>")
class BNIInfoPaymentRoutes(Resource):
    """
        Banks
        /banks/bni/payment/<account_no>
    """
    @admin_required
    def get(self, ref_number):
        """ Endpoint for getting BNI Payment info """
        response = BankServices().get_payment_status(ref_number)
        return response
    #end def

    @admin_required
    def delete(self, ref_number):
        """ Endpoint for cancelling BNI Payment """
        request_data = BNIUtilityRequestSchema.parser.parse_args(strict=True)
        account_no = request_data["account_no"]
        amount = request_data["amount"]
        response = BankServices().void_payment(ref_number, account_no, amount)
        return response
    #end def
#end class

@api.route("/bni/payment/")
class BNIPaymentRoutes(Resource):
    """
        Banks
        /banks/bni/payment/
    """
    @admin_required
    def post(self):
        """ Endpoint for executing BNI Transfer"""
        request_data = BNIUtilityDoPaymentRequestSchema.parser.parse_args(strict=True)
        response = BankServices().do_payment(request_data)
        return response
    #end def
#end class

@api.route("/bni/interbank/payment/")
class BNIInterbankPaymentRoutes(Resource):
    """
        Banks
        /banks/bni/interbank/payment/
    """
    @admin_required
    def post(self):
        """ Endpoint for executing BNI interbank transfer"""
        request_data = BNIUtilityInterbankPaymentRequestSchema.parser.parse_args(strict=True)
        response = BankServices().interbank_payment(request_data)
        return response
    #end def

    @admin_required
    def get(self):
        """ Endpoint for executing BNI interbank inquiry"""
        request_data = BNIUtilityInterbankInquiryRequestSchema.parser.parse_args(strict=True)
        response = BankServices().interbank_inquiry(request_data)
        return response
    #end def
#end class
