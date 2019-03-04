"""
    BNI Bank Helper
    _________________
    this is module to interact with BNI Virtual Account &
    Core Banking API
"""
#pylint: disable=too-many-nested-blocks
#pylint: disable=redefined-outer-name
#pylint: disable=bad-whitespace

from datetime import datetime
import time
import random
import base64
import json
import pytz
import requests
import jwt

from werkzeug.contrib.cache import SimpleCache

from app.api import db
# models
from app.api.models import ExternalLog
# configuration
from app.config import config
# exceptions
from task.bank.exceptions.general import *
# utility
from task.bank.BNI.utility import remote_call

LOGGING_CONFIG = config.Config.LOGGING_CONFIG

class VirtualAccount:
    """ This is class to interact with BNI E-Collection API"""

    BNI_ECOLLECTION_CONFIG = config.Config.BNI_ECOLLECTION_CONFIG

    BASE_URL = BNI_ECOLLECTION_CONFIG["BASE_URL"]

    TIMEZONE = pytz.timezone("Asia/Jakarta")

    def _post(self, api_name, resource_type, payload):
        if resource_type == "CREDIT":
            client_id = self.BNI_ECOLLECTION_CONFIG["CREDIT_CLIENT_ID"]
            secret_key = self.BNI_ECOLLECTION_CONFIG["CREDIT_SECRET_KEY"]
        elif resource_type == "DEBIT":
            client_id = self.BNI_ECOLLECTION_CONFIG["DEBIT_CLIENT_ID"]
            secret_key = self.BNI_ECOLLECTION_CONFIG["DEBIT_SECRET_KEY"]
        #end if

        # assign client in in payload
        payload["client_id"] = client_id
        try:
            remote_response = remote_call.post(api_name, self.BASE_URL, client_id,
                                               secret_key, payload)
        except ServicesFailed as error:
            raise RemoteCallError(error)
        return remote_response
    #end def

    def create_va(self, resource_type, params):
        """
            Function to Create Virtual Account on BNI
            args:
                resource_type -- CARDLESS/ CREDIT
                params -- payload
                session -- database session (optional)
        """
        if resource_type == "CREDIT":
            api_type = self.BNI_ECOLLECTION_CONFIG["BILLING"]
            billing_type = self.BNI_ECOLLECTION_CONFIG["CREDIT_BILLING_TYPE"]
            api_name = "CREATE_CREDIT_VA"
        elif resource_type == "DEBIT":
            api_type = self.BNI_ECOLLECTION_CONFIG["CARDLESS"]
            billing_type = self.BNI_ECOLLECTION_CONFIG["CARDLESS_BILLING_TYPE"]
            api_name = "CREATE_CARDLESS_DEBIT_VA"
        #end if

        # modify msisdn so match BNI format
        payload = {
            'type'            : api_type,
            'client_id'       : None, # set client_id in another function
            'trx_id'          : params["transaction_id"],
            'trx_amount'      : params["amount"],
            'billing_type'    : billing_type,
            'customer_name'   : params["customer_name"],
            'customer_email'  : '',
            'customer_phone'  : params["customer_phone"],
            'virtual_account' : params["virtual_account"],
            'datetime_expired': params["datetime_expired"].astimezone(self.TIMEZONE).strftime("%Y-%m-%d %H:%M:%S"),
        }

        # to match payload we need to add description on CREDIT VA
        if resource_type == "CREDIT":
            payload["description"] = ""
        #end if

        try:
            result = self._post(api_name, resource_type, payload)
        except RemoteCallError as error:
            raise ApiError(error.original_exception)
        #end try
        return result
    #end def

    def get_inquiry(self, resource_type, params):
        """
            Function to get Virtual Account Inquiry on BNI
            args:
                resource_type -- CARDLESS/ CREDIT
                params -- payload
        """
        api_name = "GET_INQUIRY"

        payload = {
            'type'     : self.BNI_ECOLLECTION_CONFIG["INQUIRY"],
            'client_id': None, # set in another function
            'trx_id'   : params["trx_id"]
        }
        try:
            result = self._post(api_name, resource_type, payload)
        except RemoteCallError as error:
            raise ApiError(error.original_exception)
        #end try
        return result
    #end def

    def update_va(self, resource_type, params):
        """
            Function to update BNI Virtual Account
            args:
                resource_type -- CREDIT/CARDLESS
                params -- payload
        """
        api_name = "UPDATE_TRANSACTION"

        response = {
            "status" : "SUCCESS",
            "data"   : {}
        }

        payload = {
            'type'             : self.BNI_ECOLLECTION_CONFIG["UPDATE"],
            'client_id'        : None,
            'trx_id'           : params["trx_id"],
            'trx_amount'       : params["amount"],
            'customer_name'    : params["customer_name"],
            'datetime_expired' : params["datetime_expired"].strftime("%Y-%m-%d %H:%M:%S"),
        }

        try:
            result = self._post(api_name, resource_type, payload)
        except RemoteCallError as error:
            raise ApiError(error.original_exception)
        #end try
        return result
    #end def
#end class

class CoreBank:
    """ This is class that handle interaction to BNI Core Banking API"""

    BNI_OPG_CONFIG = config.Config.BNI_OPG_CONFIG
    ROUTES = BNI_OPG_CONFIG["ROUTES"]
    URL = BNI_OPG_CONFIG["BASE_URL"] + ":" + BNI_OPG_CONFIG["PORT"]

    cache = SimpleCache()

    def __init__(self, access_token=None):
        """ set access token here"""
        if access_token is None:
            # if token still cached use that one if not fetch the new one
            cached_token = self.cache.get('BNI_OPG_ACCESS_TOKEN')
            if cached_token is None:
                access_token = self._get_token()
                # set token in cache
                self.cache.set('BNI_OPG_ACCESS_TOKEN', access_token, timeout= 60 * 60)
                cached_token = access_token
            #end if
            self.access_token = cached_token
        else:
            self.access_token = access_token
        #end if
    #end def

    def _create_signature(self, payload):
        signature = jwt.encode(
            payload,
            self.BNI_OPG_CONFIG["SECRET_API_KEY"],
            algorithm="HS256")
        return signature.decode("utf-8")
    #end def

    @staticmethod
    def _generate_ref_number():
        """ generate reference number matched to BNI format"""
        now = datetime.utcnow()
        value_date = now.strftime("%Y%m%d%H%M%S")
        code = random.randint(1, 99999)
        return str(value_date) + str(code)
    #end def

    @staticmethod
    def _check_response_code(response):
        """ special function to check response code according to BNI response """
        for (key, value) in response.items():
            for (key, value) in value.items():
                if key == "parameters":
                    for key, value in value.items():
                        if key == "responseCode":
                            # check response code here
                            if value != "0001":
                             # mark request as failed
                                return False
        return True
    #end def

    def _post(self, api_name, payload):
        """
            send request to BNI server and adjust everything
            according to BNI
            args :
                api_name -- Services name
                payload -- request payload
        """
        response = {
            "data" : None
        }

        # init headers here
        headers = {
            "Content-Type" : None,
        }

        # client_id in payload
        payload["clientId"] = self.BNI_OPG_CONFIG["CLIENT_NAME"]

        # add signature here
        signature = self._create_signature(payload)
        payload["signature"] = signature

        if api_name == "GET_TOKEN":
            base_64 = base64.b64encode(
                (self.BNI_OPG_CONFIG["USERNAME"] + ":"
                 + self.BNI_OPG_CONFIG["PASSWORD"]).encode("utf-8")
            )
            base_64 = base_64.decode("utf-8")
            headers["Authorization"] = "Basic {}".format(str(base_64))
            headers["Content-Type"] = "application/x-www-form-urlencoded"

            url = self.URL + self.ROUTES[api_name]
        else:
            headers["x-api-key"] = self.BNI_OPG_CONFIG["API_KEY"]
            headers["Content-Type"] = "application/json"

            # attach access_token on url here
            url = self.URL + self.ROUTES[api_name] + "?access_token=" + self.access_token

            # convert request to json
            payload = json.dumps(payload)
        #end if

        # log everything before creating request
        log = ExternalLog(request=payload,
                          resource=LOGGING_CONFIG["BNI_OPG"],
                          api_name=api_name,
                          api_type=LOGGING_CONFIG["OUTGOING"]
                         )
        db.session.add(log)

        start_time = time.time()
        try:
            r = requests.post(
                url,
                headers=headers,
                data=payload,
                timeout=LOGGING_CONFIG["TIMEOUT"]
            )
            # access the data here
            resp = r.json()
            log.save_response(resp)

            # when http status code failing we mark the request as fail
            if r.status_code != 200:
                log.set_status(False) # set as failed request
                db.session.commit()
                raise ServicesFailed("HTTP_FAILED", resp)
            #end if

            # SAVE LOG RESPONSE  RESPONE TIME
            log.save_response_time(time.time() - start_time)

            # checking response code here
            if api_name != "GET_TOKEN":
                response_status = self._check_response_code(resp)
                # if response code inside the response is not 0000 we mark it as
                # fail too
                if response_status is False:
                    log.set_status(False)
                    db.session.commit()
                    raise ServicesFailed("RESPONSE_FAILED", resp)
                #end if
            #end if
            db.session.commit()
            
            response["data"] = resp
        except requests.exceptions.Timeout as error:
            raise ServicesFailed("TIMEOUT", error)
        return response
    #end def

    def _get_token(self):
        api_name = "GET_TOKEN"
        # define response here

        # build request body here
        payload = {"grant_type" : "client_credentials"}

        # post here
        try:
            response = self._post(api_name, payload)
        except ServicesFailed as error:
            raise ApiError(error)
        #end try
        access_token = response["data"]["access_token"]
        return access_token
    #end def

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
        payload = {
            "accountNo" : account_no,
        }

        # post here
        try:
            post_resp = self._post(api_name, payload)
        except ServicesFailed as error:
            raise ApiError(error)
        #end try

        # access the data here
        response_data = post_resp["data"]["getBalanceResponse"]["parameters"]

        response["data"] = {
            "bank_account_info" : {
                "customer_name" : response_data["customerName"],
                "balance"       : response_data["accountBalance"],
            }
        }
        return response
    #end def

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
        payload = {
            "accountNo" : account_no,
        }

        try:
            post_resp = self._post(api_name, payload)
        except ServicesFailed as error:
            raise ApiError(error)
        #end try

        # access the data here
        response_data = post_resp["data"]["getInHouseInquiryResponse"]["parameters"]

        # put conditional here, if account currency is missing it means a VA
        try:
            currency = response_data["accountCurrency"]
            acc_type = "BANK_ACCOUNT"
        except KeyError:
            acc_type = "VIRTUAL_ACCOUNT"
        #end try

        response["data"] = {
            "bank_account_info" : {
                "account_no"    : response_data["accountNumber"],
                "customer_name" : response_data["customerName"],
                "status"        : response_data["accountStatus"],
                "account_type"  : response_data["accountType"],
                "type"          : acc_type, # BANK // VA
            }
        }
        return response
    #end def

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

        payment_method              = params["method"       ]
        source_account              = params["source_account"]
        destination_account         = params["account_no"   ]
        amount                      = params["amount"       ]
        destination_account_email   = params["email"        ]
        clearing_code               = params["clearing_code"]
        destination_account_name    = params["account_name" ]
        destination_account_address = params["address"      ]
        charge_mode                 = params["charge_mode"  ]

        # build payload here
        now = datetime.utcnow()
        value_date = now.strftime("%Y%m%d%H%M%S")
        currency = "IDR"

        ref_number = self._generate_ref_number()
        payload = {
            "customerReferenceNumber" : ref_number,
            "paymentMethod"           : payment_method, # 0 IN_HOUSE // 1 RTGS // 3 CLEARING
            "debitAccountNo"          : source_account, # registered BNI account
            "creditAccountNo"         : destination_account, # destination BNI / EXTERNAL BANK
            "valueDate"               : value_date, #yyyyMMddHHmmss
            "valueCurrency"           : currency, # IDR
            "valueAmount"             : amount,
            "remark"                  : "?",
            "beneficiaryEmailAddress" : destination_account_email, # must be filled if not IN_HOUSE
            "destinationBankCode"     : clearing_code, # must be filled if not IN_HOUSE
            "beneficiaryName"         : destination_account_name, # must be filled if not IN_HOUSE
            "beneficiaryAddress1"     : destination_account_address,
            "beneficiaryAddress2"     : "",
            "chargingModelId"         : charge_mode, # whos pay for it (OUR/BEN/SHA)
        }

        # post here
        # should log request and response
        try:
            post_resp = self._post(api_name, payload)
        except ServicesFailed as error:
            raise ApiError(error)
        #end if

        # access the data here
        response_data = post_resp["data"]["doPaymentResponse"]["parameters"]

        response["data"] = {
            "transfer_info" : {
                "source_account"     : response_data["debitAccountNo"],
                "destination_account": response_data["creditAccountNo"],
                "amount"             : response_data["valueAmount"],
                "ref_number"         : response_data["customerReference"],
                "bank_ref"           : response_data["bankReference"],
            },
            "request_ref" : ref_number
        }
        return response
    #end def

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
        payload = {
            "customerReferenceNumber" : request_ref,
        }

        # post here
        # should log request and response
        try:
            post_resp = self._post(api_name, payload)
        except ServicesFailed as error:
            raise ApiError(error)
        #end try

        # accessing the inner data
        response_data = post_resp["data"]["getPaymentStatusResponse"]["parameters"]["previousResponse"]
        response["data"] = {
            "payment_info" : {
                "status"             : response_data["transactionStatus"],
                "source_account"     : response_data["debitAccountNo"],
                "destination_account": response_data["creditAccountNo"],
                "amount"             : response_data["valueAmount"],
            }
        }
        return response
    #end def

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
            params["method"        ] = "0" # inhouse
            params["email"         ] = ""
            params["clearing_code" ] = ""
            params["account_name"  ] = ""
            params["address"       ] = ""
            params["charge_mode"   ] = ""
            try:
                response = self.do_payment(params)
            except ApiError as error:
                raise ApiError(error)
        else:
            try:
                interbank_response = self.get_interbank_inquiry(params)
            except ApiError as error:
                # should raise invalid account
                text = "Account {} on {} not found".format(params["account_no"], \
                                                           params["bank_code"])
                raise ApiError(error)
            #end try

            params["bank_name"] = interbank_response['data']['inquiry_info']["transfer_bank_name"]
            params["account_name"] = interbank_response['data']['inquiry_info']["account_name"]
            params["transfer_ref"] = interbank_response['data']['inquiry_info']["transfer_ref"]

            try:
                payment_response = self.get_interbank_payment(params)
            except ApiError as error:
                raise ApiError(error)
            #end try
            response["data"] = payment_response["data"]
        return response
    #end def

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
        bank_code      = params["bank_code"     ]
        account_no     = params["account_no"    ]

        # build payload here
        ref_number = self._generate_ref_number()
        payload = {
            "customerReferenceNumber": ref_number,
            "accountNum"             : source_account,
            "destinationBankCode"    : bank_code,
            "destinationAccountNum"  : account_no,
        }

        # post here
        # should log request and response
        try:
            post_resp = self._post(api_name, payload)
        except ServicesFailed as error:
            raise ApiError(error)
        #end try

        # access the data here
        response_data = post_resp["data"]["getInterbankInquiryResponse"]["parameters"]
        # check response code
        response_code = response_data["responseCode"]

        response["data"] = {
            "inquiry_info" : {
                "account_no"         : response_data["destinationAccountNum"],
                "account_name"       : response_data["destinationAccountName"],
                "transfer_bank_name" : response_data["destinationBankName"],
                "transfer_ref"       : response_data["retrievalReffNum"],
            },
            "request_ref" : ref_number
        }
        return response
    #end def

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
        account_no     = params["account_no"    ]
        account_name   = params["account_name"  ]
        bank_code      = params["bank_code"     ]
        bank_name      = params["bank_name"     ]
        amount         = params["amount"        ]
        transfer_ref   = params["transfer_ref"  ]

        # build payload here
        ref_number = self._generate_ref_number()
        payload = {
            "customerReferenceNumber": ref_number,
            "amount"                 : amount,
            "destinationAccountNum"  : account_no,
            "destinationAccountName" : account_name,
            "destinationBankCode"    : bank_code,
            "destinationBankName"    : bank_name,
            "accountNum"             : source_account,
            "retrievalReffNum"       : transfer_ref,
        }

        # post here
        # should log request and response
        try:
            post_resp = self._post(api_name, payload)
        except ServicesFailed as error:
            raise ApiError(error)
        #end try

        # access the data here
        response_data = post_resp["data"]["getInterbankPaymentResponse"]["parameters"]

        response["data"] = {
            "transfer_info" : {
                "account_no"   : response_data["destinationAccountNum"],
                "account_name" : response_data["destinationAccountName"],
                "ref_number"   : response_data["customerReffNum"],
            },
            "request_ref" : ref_number
        }
        return response
    #end def
#end class
