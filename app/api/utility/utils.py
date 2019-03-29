""" 
    UTILITY FUNCTION
"""
import json

from uuid import UUID

from app.config import config

from app.api.utility.modules.cipher import AESCipher
from app.api.utility.modules.sms_services import SmsServices
from app.api.utility.modules.notif_services import NotifServices

from app.api.error.http import *

ERROR_CONFIG = config.Config.ERROR_CONFIG
WALLET_CONFIG = config.Config.WALLET_CONFIG
SMS_SERVICES_CONFIG = config.Config.SMS_SERVICES_CONFIG
SMS_SERVICES_TEMPLATES = config.Config.SMS_SERVICES_TEMPLATES

class Sms:
    """ Class for helping sending SMS """

    def __init__(self):
        self.services = SmsServices()
    #end def

    def send(self, to, sms_type, content):
        """ build a sms template and send it using sms services """
        message = {
            "from" : SMS_SERVICES_CONFIG["FROM"],
            "text" : SMS_SERVICES_TEMPLATES[sms_type].format(str(content))
        }
        result = self.services.send_sms(to, message)
        return result
    #end def
#end class

class QR:
    """ Class For helping generating QR"""

    def generate(self, data):
        """ function to generate QR Code using AES256 Encryption """
        # convert dict to string so it be able to converted to qr code using
        qr_raw = AESCipher(WALLET_CONFIG["QR_SECRET_KEY"]).encrypt(json.dumps(data))
        return qr_raw.decode('utf-8')
    #end def

    def read(self, data):
        """ function to read encrypyed QR Code """
        qr_decrypted = AESCipher(WALLET_CONFIG["QR_SECRET_KEY"]).decrypt(data)
        return json.loads(qr_decrypted)
    #end def
#end class

class Notif:
    """ class for helping send notification"""

    def send(self, data):
        return NotifServices().send(data)


def validate_uuid(string):
    """ validate uuid"""
    try:
        uuid_object = UUID(string)
    except ValueError:
        raise BadRequest(ERROR_CONFIG["INVALID_ID"]["TITLE"],
                         ERROR_CONFIG["INVALID_ID"]["MESSAGE"])
    return uuid_object
#end def
