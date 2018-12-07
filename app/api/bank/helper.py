import pytz
import requests
import base64
import hashlib

from datetime import datetime, timedelta
from OpenSSL import crypto

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
        bank = Bank.query.filter_by(key="BNI").first()

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

    P12_KEY       = "/Users/kelvin/apps/secrets/modana.p12"

    def __init__(self):
        pass
    #end def

    def _create_signature(self, string):
        p12 = crypto.load_pkcs12(open(self.P12_KEY, 'rb').read(), "")
        priv_key = p12.get_privatekey()

        hash_string = hashlib.sha256(string).digest()
    #end def

    def get_token(self):
        API_NAME = "GET_TOKEN"

        base_64 = base64.b64encode( (self.BNI_OPG_CONFIG["USERNAME"] + ":" + self.BNI_OPG_CONFIG["PASSWORD"]).encode("utf-8") )
        headers = {
            "Content-Type" : "application/x-www-form-urlencoded",
            "Authorization": "Basic %s" % str(base_64)
        }
        payload = { "grant_type" : "client_credentials" }
        r = requests.post(self.URL + self.ROUTES["GET_TOKEN"], headers=headers, data=payload)
        if r.ok:
            response = r.json()
            access_token = response["access_token"]
            self.access_token = access_token
        else:
            return None
    #end def

    def get_balance(self):
        pass
    #end def
#end class
