"""
    Notification Services
    ________________
    This is module that to send notification
"""
import json
from datetime import datetime
import requests

from flask import current_app

# configuration
from app.config.external.notif import HR_NOTIF


class ApiError(Exception):
    """ notification api error class """

    def __init__(self, original):
        super(ApiError).__init__()
        self.original = original


class NotifServices:
    """ Notif Helper Class"""

    def _post(self, payload):
        """ execute HTTP request to Notification API """
        # build header
        headers = {"content-type": "application/json"}

        try:
            r = requests.post(
                HR_NOTIF["BASE_URL"], data=json.dumps(payload), headers=headers
            )
            current_app.logger.info(r.text)
        except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            raise ApiError(e)
        # end try
        return True

    # end def

    @staticmethod
    def _create_id_notes(key, amount):
        transfer_types = {
            "TOP_UP": "Top up sebesar {} dari Virtual Account",
            "BANK_TRANSFER": "Transfer ke Bank sebesar {}",
            "WITHDRAW": "Tarik tunai tanpa kartu sebesar {}",
            "TRANSFER": "Transfer sebesar {}",
            "PAYROLL": "Kirim gaji sebesar {}",
            "TRANSFER_FEE": "Biaya transfer sebesar {}",
            "RECEIVE_TRANSFER": "Terima transfer sebesar {}",
            "RECEIVE_PAYROLL": "Terima gaji sebesar {}",
            "AUTO_DEBIT": "Auto debit sebesar {}",
            "DEBIT_REFUND": "Pengembalian transaksi debit sebesar {}",
            "CREDIT_REFUND": "Pengembalian transaksi kredit sebesar {}",
            "AUTO_PAY": "Auto pay sebesar {}",
        }
        return transfer_types[key].format(amount)

    @staticmethod
    def _convert_type(types):
        transfer_types = {
            "TOP_UP": "top_up",
            "BANK_TRANSFER": "withdraw_to_bank",
            "WITHDRAW": "withdraw_to_atm",
            "TRANSFER": "transfer",
            "PAYROLL": "transfer",
            "TRANSFER_FEE": "transfer",
            "RECEIVE_TRANSFER": "transfer",
            "RECEIVE_PAYROLL": "transfer",
            "AUTO_DEBIT": "transfer",
            "DEBIT_REFUND": "transfer",
            "CREDIT_REFUND": "transfer",
            "AUTO_PAY": "transfer",
        }
        return transfer_types[types]

    def _generate_message(self, en_message, types, amount):
        """ generate ID and EN message that requested by HR """
        message = {"en": en_message, "id": self._create_id_notes(types, amount)}
        return message

    @staticmethod
    def _convert_date(date_time):
        return date_time.strftime("%Y-%m-%d %H:%M:%S")

    def send(self, params):
        """ execute send notifcation """
        amount = params["amount"]
        transaction_type = params["transaction_type"]
        en_message = params["en_message"]

        # need to convert message that going to be send into english and
        # indonesia
        id_en_message = self._generate_message(en_message, transaction_type, amount)

        return self._post(
            {
                "wallet_id": params["wallet_id"],
                "transaction_completed_time": self._convert_date(datetime.utcnow()),
                "amount": amount,
                "current_balance": params["balance"],
                "type": self._convert_type(transaction_type),
                "message": str(id_en_message),  # english message
            }
        )


# end class
