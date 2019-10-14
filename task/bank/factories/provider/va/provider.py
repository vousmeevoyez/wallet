"""
    BNI E-Collection Provider
    _________________________
    Handle API Execution to BNI E-collection
"""
import pytz
from datetime import datetime

from app.config.external.bank import BNI_ECOLLECTION

from task.bank.lib.provider import (
    BaseProvider
)
from task.bank.factories.factory import generate_request_response

VA_CONFIG = {
    "CREDIT": {
        "TYPE": "createbilling",
        "BILLING_TYPE": "o"
    },
    "DEBIT": {
        "TYPE": "createdebitcardless",
        "BILLING_TYPE": "j"
    }
}


class BNIVaProvider(BaseProvider):
    """ This is class to interact with BNI E-Collection API"""

    service_url = BNI_ECOLLECTION["BASE_URL"]

    TIMEZONE = pytz.timezone("Asia/Jakarta")

    def __init__(self, *args, **kwargs):
        pass

    def set(self, va_type):
        self.va_type = va_type
        request, response = generate_request_response(f"BNI_{va_type}_VA") # create request contract according to VA TYPE
        self._request_contract = request
        self._response_contract = response

    def prepare_request(self, **kwargs):
        """
            extend base prepare_request from BaseProvider so instead passing a url
            we just need to pass api_name
        """
        self.request_contract.url = self.service_url # it static
        self.request_contract.method = kwargs["method"]
        self.request_contract.payload = kwargs["payload"]


    def create_va(self, trx_id, amount, customer_name,
                  customer_phone, account_no, expire_date):
        """
            Function to Create Virtual Account on BNI
            args:
                params -- payload
        """
        # modify msisdn so match BNI format
        payload = {
            "method": "POST",
            "payload": {
                "type": VA_CONFIG[self.va_type]["TYPE"],
                "trx_id": trx_id,
                "trx_amount": amount,
                "billing_type": VA_CONFIG[self.va_type]["BILLING_TYPE"],
                "customer_name": customer_name,
                "customer_email": "",
                "customer_phone": customer_phone,
                "virtual_account": account_no,
                "datetime_expired": expire_date
                .astimezone(self.TIMEZONE)
                .strftime("%Y-%m-%d %H:%M:%S"),
            }
        }

        result = self.execute(**payload)
        return result

    def get_inquiry(self, trx_id):
        """
            Function to get Virtual Account Inquiry on BNI
            args:
                resource_type -- CARDLESS/ CREDIT
                params -- payload
        """
        payload = {
            "method": "POST",
            "payload": {
                "type": BNI_ECOLLECTION["INQUIRY"],
                "trx_id": trx_id
            }
        }

        result = self.execute(**payload)
        return result

    def update_va(self, trx_id, amount, customer_name, expire_date):
        """
            Function to update BNI Virtual Account
            args:
                resource_type -- CREDIT/CARDLESS
                params -- payload
        """
        payload = {
            "method": "POST",
            "payload":{
                "type": BNI_ECOLLECTION["UPDATE"],
                "trx_id": trx_id,
                "trx_amount": amount,
                "customer_name": customer_name,
                "datetime_expired": expire_date.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            }
        }

        result = self.execute(**payload)
        return result
