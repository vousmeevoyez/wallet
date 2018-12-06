import nexmo

from app.api.config import config

SMS_SERVICES_CONFIG    = config.Config.SMS_SERVICES_CONFIG
SMS_SERVICES_TEMPLATES = config.Config.SMS_SERVICES_TEMPLATES

class SmsHelper:

    def __init__(self):
        self.client = nexmo.Client(
            key=SMS_SERVICES_CONFIG["API_KEY"],
            secret=SMS_SERVICES_CONFIG["SECRET_KEY"]
        )
    #end def

    def send_sms(self, to, sms_type, content):
        self.client.send_message({
            "from" : SMS_SERVICES_CONFIG["FROM"],
            "to"   : to,
            "text" : SMS_SERVICES_TEMPLATES[sms_type].format(str(content))
        })
        return True
    #end def
