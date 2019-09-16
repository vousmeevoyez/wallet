"""
    BNI Bank Helper
    _________________
    this is module to interact with BNI Virtual Account &
    Core Banking API
"""
# pylint: disable=too-many-nested-blocks
# pylint: disable=redefined-outer-name
# pylint: disable=bad-whitespace

from datetime import datetime

from werkzeug.contrib.cache import SimpleCache

from task.bank.BNI.core.request import BNIOpgRequest
from task.bank.BNI.core.response import BNIOpgResponse, ResponseError

from task.bank.BNI.core.helper import (
    generate_ref_number,
    generate_url,
    authorization,
    call,
    CallError,
)

from task.bank.lib.exceptions import BaseError
# configuration
from app.config.external.bank import BNI_OPG


class ApiError(BaseError):
    """
        wrapper all the internal error inside
    """


class CoreBank:
    """ This is class that handle interaction to BNI Core Banking API"""

    cache = SimpleCache()

    def __init__(self, access_token=None):
        if access_token is None:
            # if token still cached use that one if not fetch the new one
            cached_token = self.cache.get("BNI_OPG_ACCESS_TOKEN")
            if cached_token is None:
                try:
                    access_token = authorization()
                except CallError as error:
                    raise ApiError(error.message, error.original_exception)
                # end try
                # set token in cache
                self.cache.set("BNI_OPG_ACCESS_TOKEN", access_token, timeout=60 * 60)
                cached_token = access_token
            # end if
            self.access_token = cached_token
        else:
            self.access_token = access_token
        # end if

    def _api_call(self, api_name, payload, method="POST"):
        # build request contract
        request_contract = BNIOpgRequest(
            url=generate_url(api_name, self.access_token), method=method
        )
        request_contract.payload = payload

        # build response contract
        response_contract = BNIOpgResponse

        result = call(request_contract, response_contract)
        return result

    def get_balance(self, params):
        """
            Function to check bank account balance using BNI services
            args :
                params -- account_no
        """
        response = {}

        api_name = "GET_BALANCE"

        account_no = params["account_no"]

        # payload
        payload = {"accountNo": account_no}

        # post here
        try:
            post_resp = self._api_call(api_name, payload)
        except CallError as error:
            raise ApiError(error.message, error.original_exception)

        # access the data here
        response_data = post_resp["data"]["getBalanceResponse"]["parameters"]

        response["data"] = {
            "bank_account_info": {
                "customer_name": response_data["customerName"],
                "balance": response_data["accountBalance"],
            }
        }
        return response

    def get_inhouse_inquiry(self, params):
        """
            function to call check Account inquiry that stored in BNI
            args :
                params -- account_no // BNI account number
        """
        api_name = "GET_INHOUSE_INQUIRY"

        # define response here
        response = {}

        account_no = params["account_no"]

        # build payload here
        payload = {"accountNo": account_no}

        try:
            post_resp = self._api_call(api_name, payload)
        except CallError as error:
            raise ApiError(error.message, error.original_exception)
        # end try

        # access the data here
        response_data = post_resp["data"]["getInHouseInquiryResponse"]["parameters"]

        # put conditional here, if account currency is missing it means a VA
        try:
            currency = response_data["accountCurrency"]
            acc_type = "BANK_ACCOUNT"
        except KeyError:
            acc_type = "VIRTUAL_ACCOUNT"
        # end try

        response["data"] = {
            "bank_account_info": {
                "account_no": response_data["accountNumber"],
                "customer_name": response_data["customerName"],
                "status": response_data["accountStatus"],
                "account_type": response_data["accountType"],
                "type": acc_type,  # BANK // VA
            }
        }
        return response

    # end def

    def do_payment(self, params):
        """
            function to do interbank payment
            using LLG / Clearing Method
            args :
                params -- parameter
        """
        api_name = "DO_PAYMENT"

        # define response here
        response = {}

        payment_method = params["method"]
        source_account = params["source_account"]
        destination_account = params["account_no"]
        amount = params["amount"]
        destination_account_email = params["email"]
        clearing_code = params["clearing_code"]
        destination_account_name = params["account_name"]
        destination_account_address = params["address"]
        charge_mode = params["charge_mode"]
        ref_number = params["ref_number"] or generate_ref_number()

        # build payload here
        now = datetime.utcnow()
        value_date = now.strftime("%Y%m%d%H%M%S")
        currency = "IDR"

        payload = {
            "customerReferenceNumber": ref_number,
            "paymentMethod": payment_method,  # 0 IN_HOUSE // 1 RTGS // 3 CLEARING
            "debitAccountNo": source_account,  # registered BNI account
            "creditAccountNo": destination_account,  # destination BNI / EXTERNAL BANK
            "valueDate": value_date,  # yyyyMMddHHmmss
            "valueCurrency": currency,  # IDR
            "valueAmount": amount,
            "remark": "?",
            "beneficiaryEmailAddress": destination_account_email,  # must be filled if not IN_HOUSE
            "destinationBankCode": clearing_code,  # must be filled if not IN_HOUSE
            "beneficiaryName": destination_account_name,  # must be filled if not IN_HOUSE
            "beneficiaryAddress1": destination_account_address,
            "beneficiaryAddress2": "",
            "chargingModelId": charge_mode,  # whos pay for it (OUR/BEN/SHA)
        }

        # post here
        # should log request and response
        try:
            post_resp = self._api_call(api_name, payload)
        except CallError as error:
            raise ApiError(error.message, error.original_exception)
        # end if

        # access the data here
        response_data = post_resp["data"]["doPaymentResponse"]["parameters"]

        response["data"] = {
            "transfer_info": {
                "source_account": response_data["debitAccountNo"],
                "destination_account": response_data["creditAccountNo"],
                "amount": response_data["valueAmount"],
                "ref_number": response_data["customerReference"],
                "bank_ref": response_data["bankReference"],
            },
            "request_ref": ref_number,
        }
        return response

    # end def

    def get_payment_status(self, params):
        """
            function to check payment status from DO_PAYMENT
            args:
                params -- parameter
        """
        api_name = "GET_PAYMENT_STATUS"

        # define response here
        response = {}

        request_ref = params["request_ref"]

        # build payload here
        payload = {"customerReferenceNumber": request_ref}

        # post here
        # should log request and response
        try:
            post_resp = self._api_call(api_name, payload)
        except CallError as error:
            raise ApiError(error.message, error.original_exception)
        # end try

        # accessing the inner data
        response_data = post_resp["data"]["getPaymentStatusResponse"]["parameters"][
            "previousResponse"
        ]
        response["data"] = {
            "payment_info": {
                "status": response_data["transactionStatus"],
                "source_account": response_data["debitAccountNo"],
                "destination_account": response_data["creditAccountNo"],
                "amount": response_data["valueAmount"],
            }
        }
        return response

    # end def

    def hold_amount(self, params):
        """
            function to cancel payment from HOLD_AMOUNT
            args:
                params -- parameter
        """
        api_name = "HOLD_AMOUNT"

        # define response here
        response = {}

        request_ref = params["request_ref"]
        account_no = params["account_no"]
        amount = str(params["amount"])

        # build payload here
        payload = {
            "customerReferenceNumber": request_ref,
            "accountNo": account_no,
            "amount": amount,
            "detail": "",
        }

        # post here
        # should log request and response
        try:
            post_resp = self._api_call(api_name, payload)
        except CallError as error:
            raise ApiError(error.message, error.original_exception)
        # end try

        # accessing the inner data
        response_data = post_resp["data"]["holdAmountResponse"]["parameters"]
        response["data"] = {
            "payment_info": {
                "customer_name": response_data["accountOwner"],
                "bank_ref": response_data["bankReference"],
                "ref_number": response_data["customerReference"],
            }
        }
        return response

    # end def

    def transfer(self, params):
        """
            function that wrap interbank inquiry do_payment and interbank payment
            args :
                params -- parameter
        """
        response = {}
        # if bank code is BNI then use do_payment
        if params["bank_code"] == "009":
            # adjust required parameter here and replace with empty string
            params["method"] = "0"  # inhouse
            params["email"] = ""
            params["clearing_code"] = ""
            params["account_name"] = ""
            params["address"] = ""
            params["charge_mode"] = ""
            try:
                response = self.do_payment(params)
            except ApiError as error:
                raise ApiError(error.message, error.original_exception)
        else:
            try:
                interbank_response = self.get_interbank_inquiry(params)
            except ApiError as error:
                # should raise invalid account
                text = "Account {} on {} not found".format(
                    params["account_no"], params["bank_code"]
                )
                raise ApiError(error.message, error.original_exception)
            # end try

            params["bank_name"] = interbank_response["data"]["inquiry_info"][
                "transfer_bank_name"
            ]
            params["account_name"] = interbank_response["data"]["inquiry_info"][
                "account_name"
            ]
            params["transfer_ref"] = interbank_response["data"]["inquiry_info"][
                "transfer_ref"
            ]

            try:
                payment_response = self.get_interbank_payment(params)
            except ApiError as error:
                raise ApiError(error.message, error.original_exception)
            # end try
            response["data"] = payment_response["data"]
        return response

    # end def

    def get_interbank_inquiry(self, params):
        """
            function to check inquiry OUTSIDE BNI like BCA, etc...
            args :
                params -- parameter
        """
        api_name = "GET_INTERBANK_INQUIRY"

        # define response here
        response = {}

        source_account = params["source_account"]
        bank_code = params["bank_code"]
        account_no = params["account_no"]
        ref_number = params["ref_number"] or generate_ref_number()

        # build payload here
        payload = {
            "customerReferenceNumber": ref_number,
            "accountNum": source_account,
            "destinationBankCode": bank_code,
            "destinationAccountNum": account_no,
        }

        # post here
        # should log request and response
        try:
            post_resp = self._api_call(api_name, payload)
        except CallError as error:
            raise ApiError(error.message, error.original_exception)
        # end try

        # access the data here
        response_data = post_resp["data"]["getInterbankInquiryResponse"]["parameters"]
        # check response code
        response_code = response_data["responseCode"]

        response["data"] = {
            "inquiry_info": {
                "account_no": response_data["destinationAccountNum"],
                "account_name": response_data["destinationAccountName"],
                "transfer_bank_name": response_data["destinationBankName"],
                "transfer_ref": response_data["retrievalReffNum"],
            },
            "request_ref": ref_number,
        }
        return response

    # end def

    def get_interbank_payment(self, params):
        """
            function to transfer to external bank like bca, mandiri, etc..
            args :
                params -- parameter
        """
        api_name = "GET_INTERBANK_PAYMENT"

        # define response here
        response = {}

        source_account = params["source_account"]
        account_no = params["account_no"]
        account_name = params["account_name"]
        bank_code = params["bank_code"]
        bank_name = params["bank_name"]
        amount = params["amount"]
        transfer_ref = params["transfer_ref"]
        ref_number = params["ref_number"] or generate_ref_number()

        # build payload here
        payload = {
            "customerReferenceNumber": ref_number,
            "amount": amount,
            "destinationAccountNum": account_no,
            "destinationAccountName": account_name,
            "destinationBankCode": bank_code,
            "destinationBankName": bank_name,
            "accountNum": source_account,
            "retrievalReffNum": transfer_ref,
        }

        # post here
        # should log request and response
        try:
            post_resp = self._api_call(api_name, payload)
        except CallError as error:
            raise ApiError(error.message, error.original_exception)
        # end try

        # access the data here
        response_data = post_resp["data"]["getInterbankPaymentResponse"]["parameters"]

        response["data"] = {
            "transfer_info": {
                "account_no": response_data["destinationAccountNum"],
                "account_name": response_data["destinationAccountName"],
                "ref_number": response_data["customerReffNum"],
            },
            "request_ref": ref_number,
        }
        return response

    def health_check(self):
        print("something happen")

# end class
