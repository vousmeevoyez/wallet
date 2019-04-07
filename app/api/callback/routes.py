"""
    Callback Routes
    ______________________
    this module that receive http request from callback url
"""
from marshmallow import ValidationError
from flask_restplus import Resource
from flask import request
# api
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

class BaseRoutes(Resource):
    bni_ecollection_config = config.Config.BNI_ECOLLECTION_CONFIG
    logging_config = config.Config.LOGGING_CONFIG
    error_response = config.Config.ERROR_CONFIG

@api.route('/bni/va/withdraw')
class WithdrawCallback(BaseRoutes):
    """
        Callback
        /bni/va/withdraw
    """    
    def post(self):
        """ Endpoint for receiving Withdraw Notification from BNI """

        # we received encrypted data and we need to decrypt it first
        encrypted_data = request.get_json()
        try:
            request_data = decrypt(self.bni_ecollection_config["DEBIT_CLIENT_ID"],
                                   self.bni_ecollection_config["DEBIT_SECRET_KEY"],
                                   encrypted_data["data"])

            # log every incoming callback
            external_log = ExternalLog(request=request_data,
                                       resource=self.logging_config["BNI_ECOLLECTION"],
                                       api_name="WITHDRAW_CALLBACK",
                                       api_type=self.logging_config["INGOING"])
            db.session.add(external_log)
        except DecryptError:
            # raise error
            raise BadRequest(self.error_response["INVALID_CALLBACK"]["TITLE"],
                             self.error_response["INVALID_CALLBACK"]["MESSAGE"])
        #end try

        # validate payload
        try:
            result = CallbackSchema(strict=True).validate(request_data)
        except ValidationError as error:
            raise BadRequest(self.error_response["INVALID_PARAMETER"]["TITLE"],
                             self.error_response["INVALID_PARAMETER"]["MESSAGE"],
                             error.messages)
        #end try

        # add payment channel key here to know where the request coming from
        request_data["payment_channel_key"] = "BNI_VA"
        response = CallbackServices(request_data["virtual_account"],
                                    request_data["trx_id"]).process_callback(request_data)
        # save response
        external_log.save_response(response)
        db.session.commit()

        return response
    #end def
#end class

@api.route('/bni/va/deposit')
class DepositCallback(BaseRoutes):
    """
        Callback
        /bni/va/deposit
    """  
    def post(self):
        """ Endpoint for receiving deposit Notification from BNI """

        # we received encrypted data and we need to decrypt it first
        encrypted_data = request.get_json()
        try:
            request_data = decrypt(self.bni_ecollection_config["CREDIT_CLIENT_ID"],
                                   self.bni_ecollection_config["CREDIT_SECRET_KEY"],
                                   encrypted_data["data"])

            # log every incoming callback
            external_log = ExternalLog(request=request_data,
                                       resource=self.logging_config["BNI_ECOLLECTION"],
                                       api_name="DEPOSIT_CALLBACK",
                                       api_type=self.logging_config["INGOING"])
            db.session.add(external_log)
        except DecryptError:
            raise BadRequest(self.error_response["INVALID_CALLBACK"]["TITLE"],
                             self.error_response["INVALID_CALLBACK"]["MESSAGE"])
        #end try

        try:
            result = CallbackSchema(strict=True).validate(request_data)
        except ValidationError as error:
            raise BadRequest(self.error_response["INVALID_PARAMETER"]["TITLE"],
                             self.error_response["INVALID_PARAMETER"]["MESSAGE"],
                             error.messages)
        #end try

        # add payment channel key here to know where the request coming from
        request_data["payment_channel_key"] = "BNI_VA"
        response = CallbackServices(request_data["virtual_account"],
                                    request_data["trx_id"]).process_callback(request_data)
        # save response
        external_log.save_response(response)
        db.session.commit()

        return response
    #end def
#end class
