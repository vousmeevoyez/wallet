"""
    BNI OPG Provider
    _________________
    handle request response communication with BNI OPG and provide various interface based on BNI Documentation
"""
import random
from datetime import datetime

from werkzeug.contrib.cache import SimpleCache

from app.config.external.bank import BNI_OPG

from task.bank.lib.provider import (
    BaseProvider
)

from app.api.models import Bank


class BNIOpgProvider(BaseProvider):
    """ Class that provide various BNI OPG Interface """

    service_url = BNI_OPG["BASE_URL"]
    service_port = BNI_OPG["PORT"]
    contract = "BNI_OPG"

    def __init__(self, access_token):
        super().__init__()
        self.access_token = access_token

    def api_name_to_full_url(self, api_name):
        """ convert API name into right full url """
        full_url = self.url + BNI_OPG["ROUTES"][api_name]
        full_url = full_url + "?access_token={}".format(self.access_token)
        return full_url

    def prepare_request(self, **kwargs):
        """
            extend base prepare_request from BaseProvider so instead passing a url
            we just need to pass api_name
        """
        self.request_contract.url = self.api_name_to_full_url(
            kwargs["api_name"]
        )
        self.request_contract.method = kwargs["method"]
        self.request_contract.payload = kwargs["payload"]
        return self.request_contract

    def get_balance(self, account_no):
        """
            Function to check bank account balance using BNI provider
            args :
                params -- account_no
        """
        # payload
        payload = {
            "api_name": "GET_BALANCE",
            "method": "POST",
            "payload": {
                "accountNo": account_no
            }
        }

        post_resp = self.execute(**payload)

        # access the data here
        response_data = post_resp["getBalanceResponse"]["parameters"]

        response = {
            "bank_account_info": {
                "customer_name": response_data["customerName"],
                "balance": response_data["accountBalance"],
            }
        }
        return response

    def get_inhouse_inquiry(self, account_no):
        """
            function to call check Account inquiry that stored in BNI
            args :
                params -- account_no // BNI account number
        """
        # payload
        payload = {
            "api_name": "GET_INHOUSE_INQUIRY",
            "method": "POST",
            "payload": {
                "accountNo": account_no
            }
        }

        post_resp = self.execute(**payload)

        # access the data here
        response_data = post_resp["getInHouseInquiryResponse"]["parameters"]

        # put conditional here, if account currency is missing it means a VA
        try:
            currency = response_data["accountCurrency"]
            acc_type = "BANK_ACCOUNT"
        except KeyError:
            acc_type = "VIRTUAL_ACCOUNT"
        # end try

        response = {
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

    def do_payment(self, method, source, destination, amount, email,
                   destination_bank_code, account_name, address, charge_mode,
                   ref_number):
        """
            function to do interbank payment
            using LLG / Clearing Method
            args :
                params -- parameter
        """
        # build payload here
        now = datetime.utcnow()
        value_date = now.strftime("%Y%m%d%H%M%S")
        currency = "IDR"

        payload = {
            "api_name": "DO_PAYMENT",
            "method": "POST",
            "payload": {
                "customerReferenceNumber": ref_number,
                "paymentMethod": method,  # 0 IN_HOUSE // 1 RTGS // 3 CLEARING
                "debitAccountNo": source,  # registered BNI account
                "creditAccountNo": destination,  # destination BNI / EXTERNAL BANK
                "valueDate": value_date,  # yyyyMMddHHmmss
                "valueCurrency": currency,  # IDR
                "valueAmount": amount,
                "remark": "?",
                "beneficiaryEmailAddress": email,  # must be filled if not IN_HOUSE
                "destinationBankCode": destination_bank_code,  # must be filled if not IN_HOUSE
                "beneficiaryName": account_name,  # must be filled if not IN_HOUSE
                "beneficiaryAddress1": address,
                "beneficiaryAddress2": "",
                "chargingModelId": charge_mode,  # whos pay for it (OUR/BEN/SHA)
            }
        }

        post_resp = self.execute(**payload)

        # access the data here
        response_data = post_resp["doPaymentResponse"]["parameters"]

        response = {
            "transfer_info": {
                "source_account": response_data["debitAccountNo"],
                "destination_account": response_data["creditAccountNo"],
                "amount": response_data["valueAmount"],
                "ref_number": response_data["customerReference"],
                "bank_ref": response_data["bankReference"],
            },
            "request_ref": ref_number
        }
        return response

    # end def

    def get_payment_status(self, request_ref):
        """
            function to check payment status from DO_PAYMENT
            args:
                params -- parameter
        """
        # build payload here
        payload = {
            "api_name": "GET_PAYMENT_STATUS",
            "method": "POST",
            "payload": {
                "customerReferenceNumber": request_ref
            }
        }

        post_resp = self.execute(**payload)

        # accessing the inner data
        response_data = post_resp["getPaymentStatusResponse"]["parameters"][
            "previousResponse"
        ]
        response = {
            "payment_info": {
                "status": response_data["transactionStatus"],
                "source_account": response_data["debitAccountNo"],
                "destination_account": response_data["creditAccountNo"],
                "amount": response_data["valueAmount"],
            }
        }
        return response
    # end def

    def hold_amount(self, ref_number, account_no, amount):
        """
            function to cancel payment from HOLD_AMOUNT
            args:
                params -- parameter
        """
        # build payload here
        payload = {
            "api_name": "HOLD_AMOUNT",
            "method": "POST",
            "payload": {
                "customerReferenceNumber": ref_number,
                "accountNo": account_no,
                "amount": amount,
                "detail": "",
            }
        }

        post_resp = self.execute(**payload)

        # accessing the inner data
        response_data = post_resp["holdAmountResponse"]["parameters"]
        response = {
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
        response = None
        # if bank code is BNI then use do_payment
        transfer_ref_number = params["transfer_ref_number"]
        inquiry_ref_number = params["inquiry_ref_number"]


        if params["bank_code"] == "009":
            # adjust required parameter here and replace with empty string
            params["method"] = "0"  # inhouse
            params["email"] = ""
            params["destination_bank_code"] = ""
            params["account_name"] = ""
            params["address"] = ""
            params["charge_mode"] = ""

            del params["inquiry_ref_number"]
            del params["transfer_ref_number"]
            del params["bank_code"]
            del params["destination_name"]

            params["ref_number"] = transfer_ref_number

            response = self.do_payment(**params)
        else:
            '''
            interbank_inquiry_payload = {
                "ref_number": inquiry_ref_number,
                "source": params["source"],
                "bank_code": params["bank_code"],
                "destination": params["destination"]
            }

            interbank_resp = self.get_interbank_inquiry(
                **interbank_inquiry_payload
            )

            params["bank_name"] = interbank_resp["inquiry_info"][
                "transfer_bank_name"
            ]
            params["destination_name"] = interbank_resp["inquiry_info"][
                "account_name"
            ]
            params["transfer_ref"] = interbank_resp["inquiry_info"][
                "transfer_ref"
            ]
            params["ref_number"] = transfer_ref_number

            del params["inquiry_ref_number"]
            del params["transfer_ref_number"]

            response = self.interbank_payment(**params)
            '''
            # for interbank transfer we use clearing
            # we exchange bank code with their own rtgs / clearing code
            bank = Bank.query.filter_by(code=params["bank_code"]).first()

            # adjust required parameter here and replace with empty string
            params["method"] = "2"  # CLEARING
            params["email"] = ""
            params["destination_bank_code"] = bank.rtgs
            params["account_name"] = params["destination_name"]
            params["address"] = "Puri Indah Financial Tower #0506, Jl. Puri Indah Raya No.8, RT.1/RW.2, Kembangan Sel., Kec. Kembangan, Kota Jakarta Barat, Daerah Khusus Ibukota Jakarta 11610"
            # if charge mode is blank it means by default sender is the one who
            # paid for the transfer
            params["charge_mode"] = ""

            del params["inquiry_ref_number"]
            del params["transfer_ref_number"]
            del params["bank_code"]
            del params["destination_name"]

            params["ref_number"] = transfer_ref_number

            response = self.do_payment(**params)

        return response

    # end def

    def get_interbank_inquiry(self, source, bank_code, destination,
                              ref_number):
        """
            function to check inquiry OUTSIDE BNI like BCA, etc...
            args :
                params -- parameter
        """
        # build payload here
        payload = {
            "api_name": "GET_INTERBANK_INQUIRY",
            "method": "POST",
            "payload": {
                "customerReferenceNumber": ref_number,
                "accountNum": source,
                "destinationBankCode": bank_code,
                "destinationAccountNum": destination,
            }
        }

        # post here
        post_resp = self.execute(**payload)

        # access the data here
        response_data = post_resp["getInterbankInquiryResponse"]["parameters"]

        response = {
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

    def interbank_payment(self, source, destination, destination_name,
                          bank_code, bank_name, amount, transfer_ref,
                          ref_number):
        """
            function to transfer to external bank like bca, mandiri, etc..
            args :
                params -- parameter
        """
        # build payload here
        payload = {
            "api_name": "GET_INTERBANK_PAYMENT",
            "method": "POST",
            "payload": {
                "customerReferenceNumber": ref_number,
                "amount": amount,
                "destinationAccountNum": destination,
                "destinationAccountName": destination_name,
                "destinationBankCode": bank_code,
                "destinationBankName": bank_name,
                "accountNum": source,
                "retrievalReffNum": transfer_ref,
            }
        }

        # should log request and response
        post_resp = self.execute(**payload)

        # access the data here
        response_data = post_resp["getInterbankPaymentResponse"]["parameters"]

        response = {
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


class BNIOpgProviderBuilder(BaseProvider):
    """ responsible for initializing BNI OPG Provider """

    service_url = BNI_OPG["BASE_URL"]
    service_port = BNI_OPG["PORT"]
    contract = "BNI_AUTH_OPG"
    cache = SimpleCache()

    def __init__(self):
        super().__init__()
        self._instance = None

    def __call__(self):
        if not self._instance:
            access_token = self.authorize()
            self._instance = BNIOpgProvider(access_token)
        return self._instance

    def api_name_to_full(self, api_name):
        full = self.url + BNI_OPG["ROUTES"][api_name]
        return full

    def prepare_request(self, **kwargs):
        self.request_contract.url = self.api_name_to_full(
            kwargs["api_name"]
        )
        self.request_contract.method = kwargs["method"]
        self.request_contract.payload = kwargs["payload"]
        return self.request_contract

    def authorize(self):
        payload = {
            "api_name": "GET_TOKEN",
            "method": "POST",
            "payload": {"grant_type": "client_credentials"}
        }

        # post here
        access_token = self.cache.get("BNI_OPG_ACCESS_TOKEN")
        if access_token is None:
            response = self.execute(**payload)
            access_token = response["access_token"]
            self.cache.set("BNI_OPG_ACCESS_TOKEN",
                           access_token,
                           timeout=60 * 60)
        return access_token
