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

    def _extract_error(self, obj, error_key=None):
        error_message = ""
        if type(obj) == dict:
            for key, value in obj[error_key].items():
                if key == "parameters":
                    for key, value in value.iteritems():
                        if key == "errorMessage":
                            error_message = value
        else:
            error_message = obj.message
        return error_message

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
            message = self._extract_error(error.original_exception, "getBalanceResponse")
            raise UnprocessableEntity(ERROR_CONFIG["BANK_PROCESS_FAILED"]["TITLE"],
                                      message)
        return response
    #end def

    def get_account_information(self, account_no):
        """ check host balance """
        try:
            response = CoreBank().get_inhouse_inquiry({
                "account_no" : account_no
            })
        except ApiError as error:
            message = self._extract_error(error.original_exception,
                                          "getInHouseInquiryResponse")
            raise UnprocessableEntity(ERROR_CONFIG["BANK_PROCESS_FAILED"]["TITLE"],
                                      message)
        return response
    #end def

    def get_payment_status(self, reference_number):
        """ check payment status """
        try:
            response = CoreBank().get_payment_status({
                "request_ref" : reference_number
            })
        except ApiError as error:
            message = self._extract_error(error.original_exception,
                                          "getPaymentStatusResponse")
            raise UnprocessableEntity(ERROR_CONFIG["BANK_PROCESS_FAILED"]["TITLE"],
                                      message)
        return response
    #end def

    def void_payment(self, reference_number, account_no, amount):
        """ void payment """
        try:
            response = CoreBank().hold_amount({
                "request_ref" : reference_number,
                "account_no"  : account_no,
                "amount"      : amount
            })
        except ApiError as error:
            message = self._extract_error(error.original_exception,
                                          "holdAmountResponse")
            raise UnprocessableEntity(ERROR_CONFIG["BANK_PROCESS_FAILED"]["TITLE"],
                                      message)
        return response
    #end def

    def do_payment(self, params):
        """ execute do payment """
        try:
            response = CoreBank().do_payment(params)
        except ApiError as error:
            message = self._extract_error(error.original_exception,
                                          "doPaymentResponse")
            raise UnprocessableEntity(ERROR_CONFIG["BANK_PROCESS_FAILED"]["TITLE"],
                                      message)
        return response
    #end try

    def interbank_inquiry(self, params):
        """ interbank inquiry"""
        try:
            response = CoreBank().get_interbank_inquiry(params)
        except ApiError as error:
            message = self._extract_error(error.original_exception,
                                          "getInterbankInquiryResponse")
            raise UnprocessableEntity(ERROR_CONFIG["BANK_PROCESS_FAILED"]["TITLE"],
                                      message)
        return response
    #end try

    def interbank_payment(self, params):
        """ interbank payment """
        try:
            response = CoreBank().get_interbank_payment(params)
        except ApiError as error:
            message = self._extract_error(error.original_exception,
                                          "getInterbankPaymentResponse")
            raise UnprocessableEntity(ERROR_CONFIG["BANK_PROCESS_FAILED"]["TITLE"],
                                      message)
        return response
    #end try
#end class
