import requests
import base64
import hashlib

from OpenSSL import crypto

from app        import create_app, db
from app.models import ExternalLog
from app.config import config

from .utility import remote_call


LOGGING_CONFIG = config.Config.LOGGING_CONFIG

class EcollectionHandler(object):

    BNI_ECOLLECTION_CONFIG        = config.Config.BNI_ECOLLECTION_CONFIG
    BNI_ECOLLECTION_ERROR_HANDLER = config.Config.BNI_ECOLLECTION_ERROR_HANDLER

    BASE_URL     = BNI_ECOLLECTION_CONFIG["BASE_URL_DEV"]
    SECRET_KEY   = BNI_ECOLLECTION_CONFIG["SECRET_KEY"]
    CLIENT_ID    = BNI_ECOLLECTION_CONFIG["CLIENT_ID"]

    """
    def __init__(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
    #end def
    """

    def _post(self, payload):
        remote_response = remote_call.post(self.BASE_URL, self.CLIENT_ID, self.SECRET_KEY, payload)
        return remote_response
    #end def

    def create_va(self, va_type, params):
        response = {
            "status" : "SUCCESS",
            "data"   : {}
        }

        if va_type == "CREDIT":
            api_type     = self.BNI_ECOLLECTION_CONFIG["BILLING"]
            billing_type = self.BNI_ECOLLECTION_CONFIG["CREDIT_BILLING_TYPE"]
            api_name     = "CREATE_CREDIT_VA"
        elif va_type == "CARDLESS":
            api_type     = self.BNI_ECOLLECTION_CONFIG["CARDLESS"]
            billing_type = self.BNI_ECOLLECTION_CONFIG["CARDLESS_BILLING_TYPE"]
            api_name     = "CREATE_CARDLESS_DEBIT_VA"
        #end if

        payload = {
            'type'            : api_type,
            'client_id'       : self.CLIENT_ID,
            'trx_id'          : params["trx_id"],
            'trx_amount'      : params["amount"],
            'billing_type'    : billing_type,
            'customer_name'   : params["customer_name"],
            'customer_email'  : '',
            'customer_phone'  : params["customer_phone"],
            'virtual_account' : params["virtual_account"],
            'datetime_expired': params["datetime_expired"],
            'description'     : ''
        }

        # initialize logging object
        log = ExternalLog( request=payload, resource=LOGGING_CONFIG["BNI_ECOLLECTION"], api_name=api_name)

        result = self._post(payload)
        response["data"] = result["data"]

        log.save_response(result)
        log.set_status(True)

        if result["status"] != "000":
            log.save_response(result["data"])
            log.set_status(False)

            response["status"] = "FAILED"
            response["data"  ] = self.BNI_ECOLLECTION_ERROR_HANDLER["VA_ERROR"]
        #end if

        db.session.add(log)
        db.session.commit()

        return response
    #end def

    def get_inquiry(self, params):
        API_NAME = "GET_INQUIRY"

        response = {
            "status" : "SUCCESS",
            "data"   : {}
        }

        payload = {
            'type'     : self.BNI_ECOLLECTION_CONFIG["INQUIRY"],
            'client_id': self.CLIENT_ID,
            'trx_id'   : params["trx_id"]
        }

        # initialize logging object
        log = ExternalLog(request=payload,
                          resource=LOGGING_CONFIG["BNI_ECOLLECTION"],
                          api_name=API_NAME)

        result = self._post(payload)
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

    def update_va(self, params):
        API_NAME = "UPDATE_TRANSACTION"

        response = {
            "status" : "SUCCESS",
            "data"   : {}
        }

        payload = {
            'type'             : self.BNI_ECOLLECTION_CONFIG["UPDATE"],
            'client_id'        : self.CLIENT_ID,
            'trx_id'           : params["trx_id"],
            'trx_amount'       : params["amount"],
            'customer_name'    : params["customer_name"],
            'datetime_expired' : params["datetime_expired"],
        }

        # initialize logging object
        log = ExternalLog(request=payload,
                          resource=LOGGING_CONFIG["BNI_ECOLLECTION"],
                          api_name=API_NAME)

        result = self._post(payload)
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

#end class

class OpgHandler(object):

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
