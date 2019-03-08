"""
    Callback Routes
    ______________________
    this module that receive http request from callback url
"""
from marshmallow import ValidationError
from flask_restplus import Resource
from flask import request

from app.api.callback  import api

from app.api.serializer import CallbackSchema

from app.api.callback.modules.callback_services import CallbackServices

from app.api.error.http import *

from app.config import config

from task.bank.BNI.utility.remote_call import decrypt
from task.bank.BNI.utility.remote_call import DecryptError

BNI_ECOLLECTION_CONFIG = config.Config.BNI_ECOLLECTION_CONFIG
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
        return response
    #end def
#end class
