import pytz
import requests
import base64
import hashlib

from datetime import datetime, timedelta
from jose import jws

from app.api        import db
from app.api.models import ExternalLog, VirtualAccount, Wallet, Bank, VaType
from app.api.config import config

from .utility import remote_call


LOGGING_CONFIG = config.Config.LOGGING_CONFIG
WALLET_CONFIG  = config.Config.WALLET_CONFIG

class EcollectionHelper(object):

    BNI_ECOLLECTION_CONFIG        = config.Config.BNI_ECOLLECTION_CONFIG
    BNI_ECOLLECTION_ERROR_HANDLER = config.Config.BNI_ECOLLECTION_ERROR_HANDLER

    BASE_URL = BNI_ECOLLECTION_CONFIG["BASE_URL_DEV"]

    TIMEZONE = pytz.timezone("Asia/Jakarta")

    def _post(self, resource_type, payload):
        if resource_type == "CREDIT":
            CLIENT_ID  = self.BNI_ECOLLECTION_CONFIG["CREDIT_CLIENT_ID"]
            SECRET_KEY = self.BNI_ECOLLECTION_CONFIG["CREDIT_SECRET_KEY"]
        elif resource_type == "CARDLESS":
            CLIENT_ID  = self.BNI_ECOLLECTION_CONFIG["DEBIT_CLIENT_ID"]
            SECRET_KEY = self.BNI_ECOLLECTION_CONFIG["DEBIT_SECRET_KEY"]
        #end if

        # assign client in in payload
        payload["client_id"] = CLIENT_ID

        remote_response = remote_call.post(self.BASE_URL, CLIENT_ID, SECRET_KEY, payload)
        return remote_response
    #end def

    def create_va(self, resource_type, params, session=None):
        response = {
            "status" : "SUCCESS",
            "data"   : {}
        }

        # fetch va type here
        va_type = VaType.query.filter_by(key=resource_type).first()

        if resource_type == "CREDIT":
            api_type         = self.BNI_ECOLLECTION_CONFIG["BILLING"]
            billing_type     = self.BNI_ECOLLECTION_CONFIG["CREDIT_BILLING_TYPE"]
            api_name         = "CREATE_CREDIT_VA"
            datetime_expired = datetime.now(self.TIMEZONE) + timedelta(hours=WALLET_CONFIG["CREDIT_VA_TIMEOUT"])
        elif resource_type == "CARDLESS":
            api_type         = self.BNI_ECOLLECTION_CONFIG["CARDLESS"]
            billing_type     = self.BNI_ECOLLECTION_CONFIG["CARDLESS_BILLING_TYPE"]
            api_name         = "CREATE_CARDLESS_DEBIT_VA"
            datetime_expired = datetime.now(self.TIMEZONE) + timedelta(minutes=WALLET_CONFIG["CARDLESS_VA_TIMEOUT"])
        #end if

        search_va = VirtualAccount.query.filter_by(wallet_id=int(params["wallet_id"]), va_type_id=va_type.id).first()
        if search_va != None and resource_type == "CREDIT":
            response["status"] = "FAILED"
            response["data"  ] = "VA ALREADY EXISTS"
            return response
        #end if

        # set session if empty
        if session == None:
            session = db.session
        #end if
        session.begin(subtransactions=True)

        # BANK ID FIRST
        # for now we only support BNI but more bank in future
        bank = Bank.query.filter_by(code="009").first()

        # CREATE VIRTUAL ACCOUNT ON DATABASES FIRST
        va = VirtualAccount(
            name=params["customer_name"],
            wallet_id=int(params["wallet_id"]),
            status=True,# active
            bank_id=bank.id,
            va_type_id=va_type.id,
            datetime_expired=datetime_expired
        )
        va_id  = va.generate_va_number()
        trx_id = va.generate_trx_id()

        session.add(va)

        # modify msisdn so match BNI format
        msisdn = params["customer_phone"]
        customer_phone = msisdn[1:]
        fixed = "62"
        customer_phone = fixed + customer_phone

        payload = {
            'type'            : api_type,
            'client_id'       : None, # set client_id in another function
            'trx_id'          : str(trx_id),
            'trx_amount'      : str(params["amount"]),
            'billing_type'    : billing_type,
            'customer_name'   : params["customer_name"],
            'customer_email'  : '',
            'customer_phone'  : customer_phone,
            'virtual_account' : va_id,
            'datetime_expired': datetime_expired.strftime("%Y-%m-%d %H:%M:%S"),
        }

        # to match payload we need to add description on CREDIT VA
        if resource_type == "CREDIT":
            payload["description"] = ""
        #end if

        # initialize logging object
        log = ExternalLog( request=payload,
                          resource=LOGGING_CONFIG["BNI_ECOLLECTION"],
                          api_name=api_name,
                          api_type=LOGGING_CONFIG["OUTGOING"]
                         )

        result = self._post(resource_type, payload)
        response["data"] = result["data"]

        log.save_response(result)
        log.set_status(True)

        if result["status"] != "000":
            log.save_response(result["data"])
            log.set_status(False)

            response["status"] = "FAILED"
            response["data"  ] = self.BNI_ECOLLECTION_ERROR_HANDLER["VA_ERROR"]
        #end if

        session.add(log)

        # delete if cardless VA exist so there can be only 1 VA Debit
        if resource_type == "CARDLESS" and search_va != None:
            session.delete(search_va)
        #end if

        session.commit()

        return response
    #end def

    def get_inquiry(self, resource_type, params):
        API_NAME = "GET_INQUIRY"

        response = {
            "status" : "SUCCESS",
            "data"   : {}
        }

        payload = {
            'type'     : self.BNI_ECOLLECTION_CONFIG["INQUIRY"],
            'client_id': None, # set in another function
            'trx_id'   : params["trx_id"]
        }

        # initialize logging object
        log = ExternalLog( request=payload,
                          resource=LOGGING_CONFIG["BNI_ECOLLECTION"],
                          api_name=API_NAME,
                          api_type=LOGGING_CONFIG["OUTGOING"]
                         )

        result = self._post(resource_type, payload)
        response["data"] = result["data"]

        log.save_response(result)
        log.set_status(True)

        if result["status"] != "000":
            log.save_response(result["data"])
            log.set_status(False)

            response["status"] = "FAILED"
            response["data"  ] = self.BNI_ECOLLECTION_ERROR_HANDLER["INQUIRY_ERROR"]
        #end if

        db.session.add(log)
        db.session.commit()

        return response
    #end def

    def update_va(self, resource_type, params):
        API_NAME = "UPDATE_TRANSACTION"

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

        # initialize logging object
        log = ExternalLog( request=payload,
                          resource=LOGGING_CONFIG["BNI_ECOLLECTION"],
                          api_name=API_NAME,
                          api_type=LOGGING_CONFIG["OUTGOING"]
                         )

        result = self._post(resource_type, payload)
        response["data"] = result["data"]

        log.save_response(result)
        log.set_status(True)

        if result["status"] != "000":
            log.save_response(result["data"])
            log.set_status(False)

            response["status"] = "FAILED"
            response["data"  ] = self.BNI_ECOLLECTION_ERROR_HANDLER["INQUIRY_ERROR"]
        #end if

        db.session.add(log)
        db.session.commit()

        return response
    #end def

    def recreate_va(self, params):
        response = {
            "status" : "SUCCESS",
            "data"   : {}
        }

        # modify datetime_expired so it expire
        datetime_expired = datetime.now() - timedelta(hours=WALLET_CONFIG["VA_TIMEOUT"])
        params["datetime_expired"] = datetime_expired

        # first deactivate va
        va_response = self.update_va(params)
        if va_response["status"] != "SUCCESS":
            response["status"] = va_response["status"]
            response["data"  ] = va_response["data"  ]
            return response
        #end if

        # second recreate va with same VA
        va_response = self.update_va(params)
        if va_response["status"] != "SUCCESS":
            response["status"] = va_response["status"]
            response["data"  ] = va_response["data"  ]
            return response
        #end if
    #end def

#end class

class OpgHelper(object):

    BNI_OPG_CONFIG = config.Config.BNI_OPG_CONFIG
    ROUTES         = BNI_OPG_CONFIG["ROUTES"]
    URL            = BNI_OPG_CONFIG["BASE_URL_DEV"] + ":" + BNI_OPG_CONFIG["PORT"]

    def __init__(self):
        token_resp = self._get_token()
        if token_resp["status"] == "FAILED":
            self.access_token = None
        else:
            self.access_token = token_resp["data"]["access_token"]
        #end if
    #end def

    def _create_signature(self, payload):
        signature = jws.sign(
            payload,
            self.BNI_OPG_CONFIG["SECRET_API_KEY"],
            algorithm="HS256")
        return signature
    #end def

    def _generate_ref_number(self):
        now = datetime.utcnow()
        value_date = now.strftime("%Y%m%d%H%M%S")
        code = random.randint(1,99999)
        return str(value_date) + str(code)
    #end def

    def _post(self, API_NAME, payload, access_token=None):
        response = {
            "status" : None,
            "data"   : None
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

        if API_NAME == "GET_TOKEN":
            base_64 = base64.b64encode(
                (self.BNI_OPG_CONFIG["USERNAME"] + ":" + self.BNI_OPG_CONFIG["PASSWORD"]).encode("utf-8")
            )
            base_64 = base_64.decode("utf-8")
            headers["Authorization"] = "Basic {}".format(str(base_64))
            headers["Content-Type" ] = "application/x-www-form-urlencoded"

            url = self.URL + self.ROUTES[API_NAME]
        else:
            headers["x-api-key"   ] = self.BNI_OPG_CONFIG["API_KEY"]
            headers["Content-Type"] = "application/json"

            # check if access_token is missing
            if access_token == None:
                response["status"] = "FAILED"
                response["data"  ] = "ACCESS_TOKEN_MISSING"
                return response
            #end if

            # attach access_token on url here
            url = self.URL + self.ROUTES[API_NAME] + "?access_token=" + access_token

            # convert request to json
            payload = json.dumps(payload)
        #end if

        try:
            r = requests.post(
                url,
                headers=headers,
                data=payload,
                timeout=LOGGING_CONFIG["TIMEOUT"]
            )
            # access the data here
            resp = r.json()
            if r.ok:
                response["status"] = "SUCCESS"
            else:
                response["status"] = "FAILED"
            #end if
            response["data"] = resp
        except requests.exceptions.Timeout:
            response["status"] = "FAILED"
            response["data"]   =  "REQUEST_TIMEOUT"
        except requests.exceptions.TooManyRedirects:
            response["status"] = "FAILED"
            response["data"]   =  "BAD_URL"
        except requests.exceptions.RequestException as e:
            print(str(e))
            response["status"] = "FAILED"
            response["data"]   =  "FAILURE"
        #end try
        return response
    #end def

    def _get_token(self):
        API_NAME = "GET_TOKEN"
        # define response here
        response = {
            "status" : "SUCCESS",
            "data"   : None,
        }

        # build request body here
        payload = { "grant_type" : "client_credentials" }

        # post here
        post_resp = self._post(API_NAME, payload)
        if post_resp["status"] != "SUCCESS":
            response["status"] = post_resp["status"]
            response["data"  ] = post_resp["data"]
            return response
        #end if

        # access the data here
        access_token = post_resp["data"]["access_token"]
        response["data"] = { "access_token" : access_token }

        return response
    #end def

    def get_balance(self, params, access_token=None):
        API_NAME = "GET_BALANCE"
        if access_token == None:
            access_token = self.access_token
        #end if

        # define response here
        response = {
            "status" : "SUCCESS",
            "data"   : None,
        }

        account_no = params["account_no"]

        # payload
        payload = {
            "accountNo" : account_no,
        }

        # post here
        # should log something here
        post_resp = self._post(API_NAME, payload, access_token)
        if post_resp["status"] != "SUCCESS":
            response["status"] = post_resp["status"]
            response["data"  ] = post_resp["data"]
            return response
        #end if
        # and log something here

        # access the data here
        response_data = post_resp["data"]["getBalanceResponse"]["parameters"]

        # check response_code here
        response_code = response_data["responseCode"]
        if response_code != "0001":
            response["status"] = "FAILED"
            response["data"  ] = response_data["errorMessage"]
            return response
        #end if
        response["data"] = {
            "bank_account_info" : {
                "customer_name" : response_data["customerName"],
                "balance"       : response_data["accountBalance"],
            }
        }
        return response
    #end def

    def get_inhouse_inquiry(self, params, access_token=None):
        API_NAME = "GET_INHOUSE_INQUIRY"
        if access_token == None:
            access_token = self.access_token
        #end if

        # define response here
        response = {
            "status" : "SUCCESS"
        }

        account_no = params["account_no"]

        # build payload here
        payload = {
            "accountNo" : account_no,
        }

        # post here
        post_resp = self._post(API_NAME, payload, access_token)
        if post_resp["status"] != "SUCCESS":
            response["status"] = post_resp["status"]
            response["data"  ] = post_resp["data"]
            return response
        #end if

        # access the data here
        response_data = post_resp["data"]["getInHouseInquiryResponse"]["parameters"]
        # check response code
        response_code = response_data["responseCode"]
        if response_code != "0001":
            response["status"] = "FAILED"
            response["data"  ] = response_data["errorMessage"]
            return response
        #end if

        # put conditional here, if account currency is missing it means a VA
        try:
            currency = response_data["accountCurrency"]
            acc_type = "BANK_ACCOUNT"
        except:
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

    def do_payment(self, params, access_token=None):
        API_NAME = "DO_PAYMENT"
        if access_token == None:
            access_token = self.access_token
        #end if

        # define response here
        response = {
            "status" : "SUCCESS"
        }

        payment_method              = params["payment_method"     ]
        source_account              = params["source_account"     ]
        destination_account         = params["destination_account"]
        amount                      = params["amount"             ]
        destination_account_email   = params["email"              ]
        clearing_code               = params["clearing_code"      ]
        destination_account_name    = params["account_name"       ]
        destination_account_address = params["address"            ]
        charge_mode                 = params["charge_mode"        ]

        # convert payment method
        if payment_method == "IN_HOUSE":
            payment_method = "0"
        elif payment_method == "RTGS":
            payment_method = "1"
        elif payment_method == "CLEARING":
            payment_method = "3"
        #end if

        # convert charge mode
        if charge_mode == "SOURCE":
            charge_mode = "OUR"
        elif charge_mode == "DESTINATION":
            charge_mode = "BEN"
        elif charge_mode == "SPLIT":
            charge_mode = "SHA"
        #end if

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
        post_resp = self._post(API_NAME, payload, access_token)
        if post_resp["status"] != "SUCCESS":
            response["status"] = post_resp["status"]
            response["data"  ] = post_resp["data"]
            return response
        #end if

        # access the data here
        response_data = post_resp["data"]["doPaymentResponse"]["parameters"]
        # check response code here
        response_code = response_data["responseCode"]
        if response_code != "0001":
            response["status"] = "FAILED"
            response["data"  ] = response_data["errorMessage"]
            return response
        #end if

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

    def get_payment_status(self, params, access_token=None):
        API_NAME = "GET_PAYMENT_STATUS"

        if access_token == None:
            access_token = self.access_token
        #end if

        # define response here
        response = {
            "status" : "SUCCESS"
        }

        request_ref = params["request_ref"]

        # build payload here
        payload = {
            "customerReferenceNumber" : request_ref,
        }

        # post here
        # should log request and response
        post_resp = self._post(API_NAME, payload, access_token)
        if post_resp["status"] != "SUCCESS":
            response["status"] = post_resp["status"]
            response["data"  ] = post_resp["data"]
            return response
        #end if

        # access the data here
        response_data = post_resp["data"]["getPaymentStatusResponse"]["parameters"]
        # check response code here
        response_code = response_data["responseCode"]
        if response_code != "0001":
            response["status"] = "FAILED"
            response["data"  ] = response_data["errorMessage"]
            return response
        #end if

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

    def get_interbank_inquiry(self, params, access_token=None):
        API_NAME = "GET_INTERBANK_INQUIRY"

        if access_token == None:
            access_token = self.access_token
        #end if

        # define response here
        response = {
            "status" : "SUCCESS"
        }

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
        post_resp = self._post(API_NAME, payload, access_token)
        if post_resp["status"] != "SUCCESS":
            response["status"] = post_resp["status"]
            response["data"  ] = post_resp["data"]
            return response
        #end if

        # access the data here
        response_data = post_resp["data"]["getInterbankInquiryResponse"]["parameters"]
        # check response code
        response_code = response_data["responseCode"]
        if response_code != "0001":
            response["status"] = "FAILED"
            response["data"  ] = response_data["errorMessage"]
            return response
        #end if
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

    def get_interbank_payment(self, params, access_token=None):
        API_NAME = "GET_INTERBANK_PAYMENT"

        if access_token == None:
            access_token = self.access_token
        #end if

        # define response here
        response = {
            "status" : "SUCCESS"
        }

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
        post_resp = self._post(API_NAME, payload, access_token)
        if post_resp["status"] != "SUCCESS":
            response["status"] = post_resp["status"]
            response["data"  ] = post_resp["data"]
            return response
        #end if

        # access the data here
        response_data = post_resp["data"]["getInterbankPaymentResponse"]["parameters"]
        # check response code
        response_code = response_data["responseCode"]
        if response_code != "0001":
            response["status"] = "FAILED"
            response["data"  ] = response_data["errorMessage"]
            return response
        #end if

        response["data"] = {
            "transfer_info" : {
                "account_no"         : response_data["destinationAccountNum"],
                "account_name"       : response_data["destinationAccountName"],
                "ref_number"         : response_data["customerReffNum"],
            },
            "request_ref" : ref_number
        }
        return response
    #end def
#end class
