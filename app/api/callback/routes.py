"""
    Callback Routes
    ______________________
    this module that receive http request from callback url
"""
import json
from flask import current_app

# api
from app.api.core import Routes
from app.api.callback import api

# serializer
from app.api.serializer import CallbackSchema

# services
from app.api.callback.modules.callback_services import CallbackServices

# error
from app.api.error.http import BadRequest

# configuration
from app.config.external.bank import BNI_ECOLLECTION
from app.api.error.message import RESPONSE as error_response

# remote call
from task.bank.BNI.va.BniEnc3 import BniEnc, BNIVADecryptError


class Callback(Routes):
    """
        Base Callback
    """

    client_id = None
    secret_key = None
    traffic_type = None

    __serializer__ = CallbackSchema()

    def preprocess(self, payload):
        try:
            payload = BniEnc().decrypt(
                payload["data"],
                self.client_id,
                self.secret_key
            )
            payload = json.loads(payload)
        except BNIVADecryptError:
            # raise error
            raise BadRequest(
                error_response["INVALID_CALLBACK"]["TITLE"],
                error_response["INVALID_CALLBACK"]["MESSAGE"],
            )
        # end try
        return payload

    # end def

    def post(self):
        """ Endpoint for receiving Withdraw Notification from BNI """
        request_data = self.serialize(self.payload(raw=True))

        current_app.logger.info("Request: {}".format(request_data))

        # add payment channel key here to know where the request coming from
        request_data["payment_channel_key"] = "BNI_VA"
        response = CallbackServices(
            request_data["virtual_account"], request_data["trx_id"],
            self.traffic_type
        ).process_callback(request_data)

        return response


@api.route("/bni/va/withdraw")
class WithdrawCallback(Callback):
    """
        Callback
        /bni/va/withdraw
    """

    client_id = BNI_ECOLLECTION["DEBIT_CLIENT_ID"]
    secret_key = BNI_ECOLLECTION["DEBIT_SECRET_KEY"]
    traffic_type = "OUT"


@api.route("/bni/va/deposit")
class DepositCallback(Callback):
    """
        Callback
        /bni/va/deposit
    """

    client_id = BNI_ECOLLECTION["CREDIT_CLIENT_ID"]
    secret_key = BNI_ECOLLECTION["CREDIT_SECRET_KEY"]
    traffic_type = "IN"
