"""
    Sms Services
    ________________
    This is module that contain interact with sms gateway services
"""
import time
import json
import requests

from app.api import db
# helper
from app.api.utility.modules.cipher import AESCipher
# models
from app.api.models import ExternalLog
# configuration
from app.config import config

WALLET_CONFIG = config.Config.WALLET_CONFIG
LOGGING_CONFIG = config.Config.LOGGING_CONFIG
SMS_SERVICES_CONFIG = config.Config.SMS_SERVICES_CONFIG

class ApiError(Exception):
    """ raised when api error happened"""
    def __init__(self, original_exception):
        super().__init__(original_exception)
        self.original_exception = original_exception
        
class SmsError(ApiError):
    """ raised when sms error """

class SmsServices:
    """ SMS Helper Class"""
    def _post(self, api_name, payload):
        # build header
        headers = {
            "content-type": "application/json"
        }
        headers["Authorization"] = "Bearer {}".format(SMS_SERVICES_CONFIG["API_KEY"])

        result = True
        try:
            # build external logging object here
            log = ExternalLog(request=payload,
                              resource=LOGGING_CONFIG["WAVECELL"],
                              api_name=api_name,
                              api_type=LOGGING_CONFIG["OUTGOING"]
                             )
            db.session.add(log)
            # start measuring time here
            start_time = time.time()
            r = requests.post(
                SMS_SERVICES_CONFIG["BASE_URL"],
                data=json.dumps(payload),
                headers=headers,
            )
            if r.status_code != 200:
                # flag request as failed
                log.set_status(False)
                result = False
            #end if
            log.save_response(r.json())
            log.save_response_time(time.time() - start_time)

            db.session.commit()
        except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            raise ApiError(e)
        #end try
        return result
    #end def

    def send_sms(self, to, message):
        """ To send sms to specific msisdn """
        api_name = "SEND_SMS_SINGLE"
        # build payload
        payload = {
            "source"     : message["from"],
            "destination": to,
            "text"       : message["text"],
            "encoding"   : "AUTO"
        }

        try:
            result = self._post(api_name, payload)
        except ApiError as e:
            raise SmsError(e)
        else:
            return result
    #end def
#end class