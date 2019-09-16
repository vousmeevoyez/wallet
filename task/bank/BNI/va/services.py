"""
    BNI Bank Helper
    _________________
    this is module to interact with BNI Virtual Account &
    Core Banking API
"""
# pylint: disable=too-many-nested-blocks
# pylint: disable=redefined-outer-name
# pylint: disable=bad-whitespace

import pytz

# configuration
from app.config.external.bank import BNI_ECOLLECTION

from task.bank.BNI.va.request import (
    BNIEcollectionCreditRequest,
    BNIEcollectionDebitRequest,
)
from task.bank.BNI.va.response import (
    BNIEcollectionCreditResponse,
    BNIEcollectionDebitResponse,
    ResponseError,
)

# imported for health check
from task.bank.lib.request import HTTPRequest
from task.bank.lib.response import HTTPResponse
from task.bank.lib.exceptions import BaseError

from task.bank.lib.remote_call import RemoteCall, RemoteCallError


class RequestError(BaseError):
    """
        raise when we failed to execute HTTP call either caused by response or
        cause by network
        not intended to consume by client
    """


class ApiError(BaseError):
    """
        wrapper all the internal error inside
    """


class VirtualAccount:
    """ This is class to interact with BNI E-Collection API"""

    TIMEZONE = pytz.timezone("Asia/Jakarta")

    def __init__(self, resource):
        self._prepare_request(resource)

    def _prepare_request(self, resource):
        # determine which contract that we use for particular request
        self.resource = resource
        if self.resource == "CREDIT":
            self.req_contract = BNIEcollectionCreditRequest
            self.res_contract = BNIEcollectionCreditResponse
        elif self.resource == "DEBIT":
            self.req_contract = BNIEcollectionDebitRequest
            self.res_contract = BNIEcollectionDebitResponse
        # end if

        # prepare base url
        self.url = BNI_ECOLLECTION["BASE_URL"]

    def _post(self, payload):
        # assign client in in payload
        try:
            request = self.req_contract(url=self.url, method="POST")
            request.payload = payload

            response = RemoteCall(request, self.res_contract).call()
        except (RemoteCallError, ResponseError) as error:
            raise RequestError(error.message, error.original_exception)
        return response

    def create_va(self, params):
        """
            Function to Create Virtual Account on BNI
            args:
                resource_type -- CARDLESS/ CREDIT
                params -- payload
                session -- database session (optional)
        """
        if self.resource == "CREDIT":
            api_type = BNI_ECOLLECTION["BILLING"]
            billing_type = BNI_ECOLLECTION["BILLING_TYPE"]["DEPOSIT"]
        elif self.resource == "DEBIT":
            api_type = BNI_ECOLLECTION["CARDLESS"]
            billing_type = BNI_ECOLLECTION["BILLING_TYPE"]["WITHDRAW"]

        # modify msisdn so match BNI format
        payload = {
            "type": api_type,
            "trx_id": params["transaction_id"],
            "trx_amount": params["amount"],
            "billing_type": billing_type,
            "customer_name": params["customer_name"],
            "customer_email": "",
            "customer_phone": params["customer_phone"],
            "virtual_account": params["virtual_account"],
            "datetime_expired": params["datetime_expired"]
            .astimezone(self.TIMEZONE)
            .strftime("%Y-%m-%d %H:%M:%S"),
        }

        # to match payload we need to add description on CREDIT VA
        if self.resource == "CREDIT":
            payload["description"] = ""

        try:
            result = self._post(payload)
        except RequestError as error:
            raise ApiError(error.message, error.original_exception)
        return result

    def get_inquiry(self, trx_id):
        """
            Function to get Virtual Account Inquiry on BNI
            args:
                resource_type -- CARDLESS/ CREDIT
                params -- payload
        """
        payload = {"type": BNI_ECOLLECTION["INQUIRY"], "trx_id": trx_id}
        try:
            result = self._post(payload)
        except RequestError as error:
            raise ApiError(error.message, error.original_exception)
        return result

    def update_va(self, params):
        """
            Function to update BNI Virtual Account
            args:
                resource_type -- CREDIT/CARDLESS
                params -- payload
        """
        payload = {
            "type": BNI_ECOLLECTION["UPDATE"],
            "client_id": None,
            "trx_id": params["trx_id"],
            "trx_amount": params["amount"],
            "customer_name": params["customer_name"],
            "datetime_expired": params["datetime_expired"].strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }

        try:
            result = self._post(payload)
        except RequestError as error:
            raise ApiError(error.message, error.original_exception)
        return result

    @staticmethod
    def health_check():
        """
            function to check BNI Virtual Account Services
        """
        # assign client in in payload
        try:
            request = HTTPRequest(url=BNI_ECOLLECTION["BASE_URL"], method="GET")
            response = HTTPResponse
            response = RemoteCall(request, response).call()
        except (RemoteCallError, ResponseError) as error:
            raise ApiError(error.message, error.original_exception)

        health_http_status = 200
        if "status" not in response:
            health_http_status = 500
        return health_http_status
