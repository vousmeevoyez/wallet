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
from app.api.const import ERROR as error_response

# http error
from app.lib.http_error import UnprocessableEntity

# BNI API
from task.bank.factories.provider.factory import generate_provider
from task.bank.lib.provider import ProviderError
from task.bank.lib.helper import extract_error


class BankServices:
    """ Bank Services Class"""

    @staticmethod
    def get_banks():
        """ return all bank available"""
        response = {}

        banks = Bank.query.filter_by(status=True).all()

        response["data"] = BankSchema(many=True).dump(banks).data
        return response

    def get_host_balance(self, account_no):
        """ check host balance """
        try:
            provider = generate_provider("BNI_OPG")
            response = provider.get_balance(account_no)
        except ProviderError as error:
            message = extract_error(error)
            raise UnprocessableEntity(
                error_response["BANK_PROCESS_FAILED"]["TITLE"], message
            )
        return response

    def get_account_information(self, account_no):
        """ check account information """
        try:
            provider = generate_provider("BNI_OPG")
            response = provider.get_inhouse_inquiry(account_no)
        except ProviderError as error:
            message = extract_error(error)
            raise UnprocessableEntity(
                error_response["BANK_PROCESS_FAILED"]["TITLE"], message
            )
        return response

    def get_payment_status(self, reference_number):
        """ check payment status """
        try:
            provider = generate_provider("BNI_OPG")
            response = provider.get_payment_status(reference_number)
        except ProviderError as error:
            message = extract_error(error)
            raise UnprocessableEntity(
                error_response["BANK_PROCESS_FAILED"]["TITLE"], message
            )
        return response

    def do_payment(self, params):
        """ execute do payment """
        try:
            provider = generate_provider("BNI_OPG")
            response = provider.do_payment(**params)
        except ProviderError as error:
            message = extract_error(error)
            raise UnprocessableEntity(
                error_response["BANK_PROCESS_FAILED"]["TITLE"], message
            )
        return response

    def interbank_inquiry(self, params):
        """ interbank inquiry"""
        try:
            provider = generate_provider("BNI_OPG")
            response = provider.get_interbank_inquiry(**params)
        except ProviderError as error:
            message = extract_error(error)
            raise UnprocessableEntity(
                error_response["BANK_PROCESS_FAILED"]["TITLE"], message
            )
        return response

    def interbank_payment(self, params):
        """ interbank payment """
        try:
            provider = generate_provider("BNI_OPG")
            response = provider.get_interbank_payment(**params)
        except ProviderError as error:
            message = extract_error(error)
            raise UnprocessableEntity(
                error_response["BANK_PROCESS_FAILED"]["TITLE"], message
            )
        # end try
        return response
