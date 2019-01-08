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
from app.api.errors     import bad_request, internal_error, request_not_found
from app.api.config     import config
from app.api.bank.handler import BankHandler

RESPONSE_MSG = config.Config.RESPONSE_MSG

class BankServices:
    """ Bank Services Class"""

    def __init__(self):
        pass
    #end def

    def get_banks(self):
        """ return all bank available"""
        response = {}

        # only show active bank
        banks = Bank.query.filter_by(status=True).all()

        response["data"] = BankSchema(many=True).dump(banks).data
        return response
    #end def

    def check_balance(self, master_id):
        """ check master account balance on certain bank """
        response = {}

        # only BNI now supported
        params = {"account_no" : master_id}
        result = BankHandler("BNI").dispatch("CHECK_BALANCE", params)
        if result["status"] != "SUCCESS":
            return bad_request(result["data"])
        #end if

        host_name = result["data"]["bank_account_info"]["customer_name"]
        balance = result["data"]["bank_account_info"]["balance"]

        response["data"] = {
            "host_name" : host_name,
            "balance"   : balance
        }
        return response
    #end def
#end class
