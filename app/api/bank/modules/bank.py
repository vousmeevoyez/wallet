import traceback
from datetime import datetime, timedelta

from flask          import request, jsonify

from app.api            import db
from app.api.models     import Bank
from app.api.serializer import BankSchema
from app.api.errors     import bad_request, internal_error, request_not_found
from app.api.config     import config
from app.api.bank       import helper

RESPONSE_MSG = config.Config.RESPONSE_MSG

class BankController:

    def __init__(self):
        pass
    #end def

    def get_banks(self, params):
        response = {}

        # only show active bank
        banks = Bank.query.filter_by(status=True).all()

        response["data"] = BankSchema(many=True).dump(banks).data
        return response
    #end def

    def check_balance(self, master_id):
        response = {}

        result = helper.OpgHelper().get_balance({
            "account_no" : master_id
        })
        if result["status"] != "SUCCESS":
            return bad_request(result["data"])
        #end if

        host_name = result["data"]["bank_account_info"]["customer_name"]
        balance   = result["data"]["bank_account_info"]["balance"]

        response["data"] = {
            "host_name" : customer_name,
            "balance"   : balance
        }
        return response
    #end def
#end class
