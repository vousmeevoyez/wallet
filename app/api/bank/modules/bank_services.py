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

class BankServices:
    """ Bank Services Class"""

    def get_banks(self):
        """ return all bank available"""
        response = {}

        banks = Bank.query.filter_by(status=True).all()

        response["data"] = BankSchema(many=True).dump(banks).data
        return response
    #end def

    def check_balance(self, master_id):
        """ check master account balance on certain bank """
        response = {}

        # only BNI now supported
        response["data"] = {
            "host_name" : host_name,
            "balance"   : balance
        }
        return response
    #end def
#end class
