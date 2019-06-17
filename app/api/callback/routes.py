"""
    Callback Routes
    ______________________
    this module that receive http request from callback url
"""
from marshmallow import ValidationError
from flask import request
# api
from app.api.core import Routes
from app.api import db
from app.api.callback  import api
# models
from app.api.models import ExternalLog
# serializer
from app.api.serializer import CallbackSchema
# services
from app.api.callback.modules.callback_services import CallbackServices
# error
from app.api.error.http import *
# configuration
from app.config import config
# remote call
from task.bank.BNI.utility.remote_call import decrypt
from task.bank.BNI.utility.remote_call import DecryptError

@api.route('/bni/va/withdraw')
class WithdrawCallback(Routes):
    """
        Callback
        /bni/va/withdraw
    """

    __serializer__ = CallbackSchema()

    bni_ecollection_config = config.Config.BNI_ECOLLECTION_CONFIG
    logging_config = config.Config.LOGGING_CONFIG

    def preprocess(self, payload):
        try:
            payload = decrypt(self.bni_ecollection_config["DEBIT_CLIENT_ID"],
                                   self.bni_ecollection_config["DEBIT_SECRET_KEY"],
                                   payload["data"])
        except DecryptError:
            # raise error
            raise BadRequest(self.error_response["INVALID_CALLBACK"]["TITLE"],
                             self.error_response["INVALID_CALLBACK"]["MESSAGE"])
        #end try
        return payload
    # end def


    def post(self):
        """ Endpoint for receiving Withdraw Notification from BNI """
        request_data = self.serialize(self.payload(raw=True))

        # log every incoming callback
        external_log = ExternalLog(request=request_data,
                                   resource=self.logging_config["BNI_ECOLLECTION"],
                                   api_name="WITHDRAW_CALLBACK",
                                   api_type=self.logging_config["INGOING"])
        db.session.add(external_log)

        # add payment channel key here to know where the request coming from
        request_data["payment_channel_key"] = "BNI_VA"
        response = CallbackServices(
            request_data["virtual_account"], request_data["trx_id"], "OUT"
        ).process_callback(request_data)

        # save response
        external_log.save_response(response)
        db.session.commit()

        return response
    #end def
#end class

@api.route('/bni/va/deposit')
class DepositCallback(Routes):
    """
        Callback
        /bni/va/deposit
    """

    __serializer__ = CallbackSchema()

    bni_ecollection_config = config.Config.BNI_ECOLLECTION_CONFIG
    logging_config = config.Config.LOGGING_CONFIG

    def preprocess(self, payload):
        try:
            payload = decrypt(self.bni_ecollection_config["CREDIT_CLIENT_ID"],
                                   self.bni_ecollection_config["CREDIT_SECRET_KEY"],
                                   payload["data"])
        except DecryptError:
            # raise error
            raise BadRequest(self.error_response["INVALID_CALLBACK"]["TITLE"],
                             self.error_response["INVALID_CALLBACK"]["MESSAGE"])
        #end try
        return payload
    # end def

    def post(self):
        """ Endpoint for receiving deposit Notification from BNI """
        request_data = self.serialize(self.payload(raw=True))

        # log every incoming callback
        external_log = ExternalLog(request=request_data,
                                   resource=self.logging_config["BNI_ECOLLECTION"],
                                   api_name="DEPOSIT_CALLBACK",
                                   api_type=self.logging_config["INGOING"])
        db.session.add(external_log)

        # add payment channel key here to know where the request coming from
        request_data["payment_channel_key"] = "BNI_VA"
        response = CallbackServices(
            request_data["virtual_account"], request_data["trx_id"], "IN"
        ).process_callback(request_data)
        # save response
        external_log.save_response(response)
        db.session.commit()

        return response
    #end def
#end class
