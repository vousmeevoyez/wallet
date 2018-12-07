import json
import requests

from app.api.config import config

SMS_SERVICES_CONFIG    = config.Config.SMS_SERVICES_CONFIG
SMS_SERVICES_TEMPLATES = config.Config.SMS_SERVICES_TEMPLATES
SMS_OTP_ERRORS         = config.Config.SMS_OTP_ERRORS

class SmsHelper:

    def __init__(self):
        pass
    #end def

    def _post(self, payload):
        # build header
        headers = {
            "content-type": "application/json"
        }
        headers["Authorization"] = "Bearer {}".format(SMS_SERVICES_CONFIG["API_KEY"])

        try:
            r = requests.post(
                SMS_SERVICES_CONFIG["BASE_URL"],
                data=json.dumps(payload),
                headers=headers,
            )
            if r.status_code != 200:
                return "REQUEST_FAILED"
        except requests.exceptions.Timeout:
            return "REQUEST_TIMEOUT"
        except requests.exceptions.TooManyRedirects:
            return "BAD_URL"
        except requests.exceptions.RequestException as e:
            print(str(e))
            return "FAILURE"
        #end try

        return "REQUEST_SUCCESS"
    #end def

    def send_sms(self, to, sms_type, content):
        response = {
            "status" : "SUCCESS",
            "data"   : None
        }
        # build payload
        payload = {
            "source"     : SMS_SERVICES_CONFIG["FROM"],
            "destination": to,
            "text"       : SMS_SERVICES_TEMPLATES[sms_type].format(str(content)),
            "encoding"   : "AUTO"
        }

        resp = self._post(payload)
        if resp == "REQUEST_FAILED":
            response["status"] = "FAILED"
            response["data"  ] = SMS_OTP_ERRORS["FAILURE"]
            return response
        elif resp == "REQUEST_TIMEOUT":
            response["status"] = "FAILED"
            response["data"  ] = SMS_OTP_ERRORS["TIMEOUT"]
            return response
        elif resp == "BAD_URL":
            response["status"] = "FAILED"
            response["data"  ] = SMS_OTP_ERRORS["REDIRECT"]
            return response
        elif resp == "EXCEPTION":
            response["status"] = "FAILED"
            response["data"  ] = SMS_OTP_ERRORS["EXCEPTION"]
            return response
        #end if
        return response
    #end def
#end class
