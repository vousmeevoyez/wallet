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

from app.api.error.http import *
from task.bank.exceptions.general import *

ERROR_CONFIG = config.Config.ERROR_CONFIG

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
        try:
            response = CoreBank().get_balance({
                "account_no" : account_no
            })
        except ApiError as error:
            print(error)
            raise UnprocessableEntity(ERROR_CONFIG["BANK_PROCESS_FAILED"]["TITLE"],
                                      ERROR_CONFIG["BANK_PROCESS_FAILED"]["MESSAGE"])
        return response
    #end def

    def get_account_information(self, account_no):
        """ check host balance """
        try:
            response = CoreBank().get_inhouse_inquiry({
                "account_no" : account_no
            })
        except ApiError as error:
            print(error)
            raise UnprocessableEntity(ERROR_CONFIG["BANK_PROCESS_FAILED"]["TITLE"],
                                      ERROR_CONFIG["BANK_PROCESS_FAILED"]["MESSAGE"])
        return response
    #end def

    def get_payment_status(self, reference_number):
        """ check payment status """
        try:
            response = CoreBank().get_payment_status({
                "request_ref" : reference_number
            })
        except ApiError as error:
            print(error)
            raise UnprocessableEntity(ERROR_CONFIG["BANK_PROCESS_FAILED"]["TITLE"],
                                      ERROR_CONFIG["BANK_PROCESS_FAILED"]["MESSAGE"])
        return response
    #end def

    def void_payment(self, reference_number):
        """ check payment status """
        try:
            response = CoreBank().get_payment_status({
                "request_ref" : reference_number
            })
        except ApiError as error:
            print(error)
            raise UnprocessableEntity(ERROR_CONFIG["BANK_PROCESS_FAILED"]["TITLE"],
                                      ERROR_CONFIG["BANK_PROCESS_FAILED"]["MESSAGE"])
        return response
    #end def
#end class
