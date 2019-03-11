"""
    Bank Services
    _______________
    this is module that serve request from bank resources
"""
import traceback

from flask import request, jsonify

from app.api            import db
from app.api.models     import Bank
from app.api.serializer import BankSchema
from app.config     import config

from task.bank.BNI.helper import CoreBank

class BankServices:
    """ Bank Services Class"""

    def get_banks(self):
        """ return all bank available"""
        response = {}

        banks = Bank.query.filter_by(status=True).all()

        response["data"] = BankSchema(many=True).dump(banks).data
        return response
    #end def

    """
        BNI
    """
    def get_host_balance(self, account_no):
        """ check host balance """
        result = CoreBank().get_balance({
            "account_no" : account_no
        })
        return result
    #end def

    def get_account_information(self, account_no):
        """ check host balance """
        result = CoreBank().get_inhouse_inquiry({
            "account_no" : account_no
        })
        return result
    #end def

    def get_payment_status(self, reference_number):
        """ check payment status """
        result = CoreBank().get_payment_status({
            "request_ref" : reference_number
        })
        return result
    #end def

    def void_payment(self, reference_number):
        """ check payment status """
        result = CoreBank().get_payment_status({
            "request_ref" : reference_number
        })
        return result
    #end def
#end class
