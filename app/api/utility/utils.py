"""
    UTILITY FUNCTION
"""
#pylint: disable=no-name-in-module
#pylint: disable=invalid-name
#pylint: disable=no-self-use
#pylint: disable=too-few-public-methods
import json

from uuid import UUID

# const
from app.api.const import WALLET
from app.config.external.sms import WAVECELL, TEMPLATES
# error
from app.api.error.message import RESPONSE as error_response

from app.api.utility.modules.cipher import AESCipher
from app.api.utility.modules.sms_services import SmsServices
from app.api.utility.modules.notif_services import NotifServices

# exceptions
from app.api.utility.modules.cipher import DecryptError
from app.api.utility.modules.sms_services import ApiError as SmsError
from app.api.utility.modules.notif_services import ApiError as NotifError
from app.api.error.http import BadRequest


class UtilityError(Exception):
    """ base error class for utility """
    def __init__(self, original=None):
        super(UtilityError).__init__()
        self.original = original

class Sms:
    """ Class for helping sending SMS """

    def send(self, to, sms_type, content):
        """ build a sms template and send it using sms services """
        message = {
            "from" : WAVECELL["FROM"],
            "text" : TEMPLATES[sms_type].format(str(content))
        }
        try:
            result = SmsServices().send_sms(to, message)
        except SmsError as error:
            raise UtilityError(error.original)
        # end try
        return result
    #end def
#end class

class QR:
    """ Class For helping generating QR"""

    def generate(self, data):
        """ function to generate QR Code using AES256 Encryption """
        # convert dict to string so it be able to converted to qr code using
        qr_raw = AESCipher(WALLET["QR_SECRET_KEY"]).encrypt(json.dumps(data))
        return qr_raw.decode('utf-8')
    #end def

    def read(self, data):
        """ function to read encrypyed QR Code """
        try:
            qr_decrypted = AESCipher(WALLET["QR_SECRET_KEY"]).decrypt(data)
        except DecryptError as error:
            raise UtilityError()
        # end try
        return json.loads(qr_decrypted)
    #end def
#end class

class Notif:
    """ class for helping send notification"""
    def send(self, data):
        """ send notification """
        try:
            result = NotifServices().send(data)
        except NotifError as error:
            raise UtilityError(error.original)
        # end try
        return result
    # end def
# end class

def validate_uuid(string):
    """ validate uuid"""
    try:
        uuid_object = UUID(string)
    except ValueError:
        raise BadRequest(error_response["INVALID_ID"]["TITLE"],
                         error_response["INVALID_ID"]["MESSAGE"])
    return uuid_object
#end def
