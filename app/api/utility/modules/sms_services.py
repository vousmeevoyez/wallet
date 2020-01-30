"""
    Sms Services
    ________________
    This is module that contain interact with sms gateway services
"""
import json
import requests

from flask import current_app

# configuration
from app.config.external.sms import WAVECELL

# const
from app.api.const import LOGGING


class ApiError(Exception):
    """ raised when api error happened"""

    def __init__(self, original):
        super().__init__(original)
        self.original = original


class SmsError(ApiError):
    """ raised when sms error """


class SmsServices:
    """ SMS Helper Class"""

    def _post(self, api_name, payload):
        # build header
        headers = {"content-type": "application/json"}
        headers["Authorization"] = "Bearer {}".format(WAVECELL["API_KEY"])

        result = True
        try:
            r = requests.post(
                WAVECELL["BASE_URL"], data=json.dumps(payload), headers=headers
            )
            if r.status_code != 200:
                result = False
            # end if
            current_app.logger.info("OTP: {}".format(r.status_code))
        except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            raise ApiError(e)
        # end try
        return result

    # end def

    def send_sms(self, to, message):
        """ To send sms to specific msisdn """
        api_name = "SEND_SMS_SINGLE"
        # build payload
        payload = {
            "source": message["from"],
            "destination": to,
            "text": message["text"],
            "encoding": "AUTO",
        }

        try:
            result = self._post(api_name, payload)
        except ApiError as e:
            raise SmsError(e)
        else:
            return result

    # end def


# end class
