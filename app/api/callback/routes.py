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

BNI_ECOLLECTION_CONFIG = config.Config.BNI_ECOLLECTION_CONFIG
LOGGING_CONFIG = config.Config.LOGGING_CONFIG
ERROR_CONFIG = config.Config.ERROR_CONFIG

@api.route('/bni/va/withdraw')
class WithdrawCallback(Resource):
    """ Class where we routes Callback Request"""
    def post(self):
        """ function that handle post withdraw """
        # we received encrypted data and we need to decrypt it first
        encrypted_data = request.get_json()
        try:
            request_data = decrypt(BNI_ECOLLECTION_CONFIG["DEBIT_CLIENT_ID"],
                                   BNI_ECOLLECTION_CONFIG["DEBIT_SECRET_KEY"],
                                   encrypted_data["data"])

            # log every incoming callback
            external_log = ExternalLog(request=request_data,
                                       resource=LOGGING_CONFIG["BNI_ECOLLECTION"],
                                       api_name="WITHDRAW_CALLBACK",
                                       api_type=LOGGING_CONFIG["INGOING"])
            db.session.add(external_log)
        except DecryptError:
            raise BadRequest(ERROR_CONFIG["INVALID_CALLBACK"]["TITLE"],
                             ERROR_CONFIG["INVALID_CALLBACK"]["MESSAGE"])
        #end try
        try:
            result = CallbackSchema(strict=True).validate(request_data)
        except ValidationError as error:
            raise BadRequest(ERROR_CONFIG["INVALID_PARAMETER"]["TITLE"],
                             ERROR_CONFIG["INVALID_PARAMETER"]["MESSAGE"],
                             error.messages)
        #end if

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
class DepositCallback(Resource):
    """ Class where we routes Callback Request"""
    def post(self):
        """ function that handle post deposit """
        # we received encrypted data and we need to decrypt it first
        encrypted_data = request.get_json()
        try:
            request_data = decrypt(BNI_ECOLLECTION_CONFIG["CREDIT_CLIENT_ID"],
                                   BNI_ECOLLECTION_CONFIG["CREDIT_SECRET_KEY"],
                                   encrypted_data["data"])

            # log every incoming callback
            external_log = ExternalLog(request=request_data,
                                       resource=LOGGING_CONFIG["BNI_ECOLLECTION"],
                                       api_name="DEPOSIT_CALLBACK",
                                       api_type=LOGGING_CONFIG["INGOING"])
            db.session.add(external_log)
        except DecryptError:
            raise BadRequest(ERROR_CONFIG["INVALID_CALLBACK"]["TITLE"],
                             ERROR_CONFIG["INVALID_CALLBACK"]["MESSAGE"])
        #end try
        try:
            result = CallbackSchema(strict=True).validate(request_data)
        except ValidationError as error:
            raise BadRequest(ERROR_CONFIG["INVALID_PARAMETER"]["TITLE"],
                             ERROR_CONFIG["INVALID_PARAMETER"]["MESSAGE"],
                             error.messages)
        #end if

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
