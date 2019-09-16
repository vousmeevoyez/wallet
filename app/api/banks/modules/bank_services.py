"""
    Bank Services
    _______________
    this is module that serve request from bank resources
"""
# pylint:disable=no-name-in-module
# models
from app.api.models import Bank

# serializer
from app.api.serializer import BankSchema

# error response
from app.api.error.message import RESPONSE as error_response

# http error
from app.api.error.http import UnprocessableEntity

# BNI API
from task.bank.BNI.core import CoreBank, ApiError


class BankServices:
    """ Bank Services Class"""

    @staticmethod
    def get_banks():
        """ return all bank available"""
        response = {}

        banks = Bank.query.filter_by(status=True).all()

        response["data"] = BankSchema(many=True).dump(banks).data
        return response

    # end def

    @staticmethod
    def _extract_error(obj, error_key=None):
        """ extract error from BNI Response format """
        error_message = ""
        if isinstance(obj.original_exception, dict):
            for key, value in obj[error_key].items():
                if key == "parameters":
                    for key, value in value.items():
                        if key == "errorMessage":
                            error_message = value
                        # end if
                    # end for
                # end if
            # end for
        # end if
        else:
            error_message = obj.message
        # end if
        return error_message

    # end def

    def get_host_balance(self, account_no):
        """ check host balance """
        try:
            response = CoreBank().get_balance({"account_no": account_no})
        except ApiError as error:
            message = self._extract_error(
                error, "getBalanceResponse"
            )
            raise UnprocessableEntity(
                error_response["BANK_PROCESS_FAILED"]["TITLE"], message
            )
        # end try
        return response

    # end def

    def get_account_information(self, account_no):
        """ check account information """
        try:
            response = CoreBank().get_inhouse_inquiry({"account_no": account_no})
        except ApiError as error:
            message = self._extract_error(
                error, "getInHouseInquiryResponse"
            )
            raise UnprocessableEntity(
                error_response["BANK_PROCESS_FAILED"]["TITLE"], message
            )
        # end try
        return response

    # end def

    def get_payment_status(self, reference_number):
        """ check payment status """
        try:
            response = CoreBank().get_payment_status({"request_ref": reference_number})
        except ApiError as error:
            message = self._extract_error(
                error, "getPaymentStatusResponse"
            )
            raise UnprocessableEntity(
                error_response["BANK_PROCESS_FAILED"]["TITLE"], message
            )
        # end try
        return response

    # end def

    def void_payment(self, reference_number, account_no, amount):
        """ void payment """
        try:
            response = CoreBank().hold_amount(
                {
                    "request_ref": reference_number,
                    "account_no": account_no,
                    "amount": amount,
                }
            )
        except ApiError as error:
            message = self._extract_error(
                error, "holdAmountResponse"
            )
            raise UnprocessableEntity(
                error_response["BANK_PROCESS_FAILED"]["TITLE"], message
            )
        # end try
        return response

    # end def

    def do_payment(self, params):
        """ execute do payment """
        try:
            response = CoreBank().do_payment(params)
        except ApiError as error:
            message = self._extract_error(error, "doPaymentResponse")
            raise UnprocessableEntity(
                error_response["BANK_PROCESS_FAILED"]["TITLE"], message
            )
        # end try
        return response

    # end try

    def interbank_inquiry(self, params):
        """ interbank inquiry"""
        try:
            response = CoreBank().get_interbank_inquiry(params)
        except ApiError as error:
            message = self._extract_error(
                error, "getInterbankInquiryResponse"
            )
            raise UnprocessableEntity(
                error_response["BANK_PROCESS_FAILED"]["TITLE"], message
            )
        # end try
        return response

    # end try

    def interbank_payment(self, params):
        """ interbank payment """
        try:
            response = CoreBank().get_interbank_payment(params)
        except ApiError as error:
            message = self._extract_error(
                error, "getInterbankPaymentResponse"
            )
            raise UnprocessableEntity(
                error_response["BANK_PROCESS_FAILED"]["TITLE"], message
            )
        # end try
        return response

    # end try


# end class
