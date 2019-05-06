"""
    Notification Services
    ________________
    This is module that to send notification
"""
import json
from datetime import datetime
import requests

# configuration
from app.config import config

NOTIF_SERVICES_CONFIG = config.Config.NOTIF_SERVICES_CONFIG

class ApiError(Exception):
    """ notification api error class """
    def __init__(self, original):
        super(ApiError).__init__()
        self.original = original

class NotifServices:
    """ Notif Helper Class"""
    def _post(self, params):
        # build header
        headers = {
            "content-type": "application/json"
        }

        payload = {
            "wallet_id": params["wallet_id"],
            "transaction_completed_time": params["created_at"],
            "amount": params["amount"],
            "type": params["type"], #top_up | withdraw_to_bank | withdraw_to_atm | transfer
            "message": params["message"]
        }

        try:
            r = requests.post(
                NOTIF_SERVICES_CONFIG["BASE_URL"],
                data=json.dumps(payload),
                headers=headers,
            )
        except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            raise ApiError(e)
        #end try
        print(r.status_code)
        return True
    #end def

    @staticmethod
    def _convert_type(types):
        transfer_types = {
            "TOP_UP"           : "top_up",
            "TRANSFER_OUT"     : "withdraw_to_bank",
            "WITHDRAW"         : "withdraw_to_atm",
            "TRANSFER_IN"      : "transfer",
            "PAYROLL"          : "transfer",
            "TRANSFER_FEE"     : "transfer",
            "RECEIVE_TRANSFER" : "transfer",
            "RECEIVE_PAYROLL"  : "transfer",
            "AUTO_DEBIT"       : "transfer",
            "REFUND"           : "transfer",
            "AUTO_PAY"         : "transfer",
        }
        return transfer_types[types]

    @staticmethod
    def _convert_date(date_time):
        return date_time.strftime("%Y-%m-%d %H:%M:%S")

    def send(self, params):
        """ execute send notifcation """
        return self._post({
            "wallet_id" : params["wallet_id"],
            "created_at": self._convert_date(datetime.utcnow()),
            "amount"    : params["amount"],
            "type"      : self._convert_type(params["transaction_type"]),
            "message"   : params["notes"],
        })
#end class
