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

from app.config import config

BNI_ECOLLECTION_CONFIG = config.Config.BNI_ECOLLECTION_CONFIG

@api.route('/bni_va/deposit')
class DepositCallback(Resource):
    """ Class where we routes Deposit Callback Request"""
    def post(self):
        """ Function to receive post request from deposit callback url"""
        # we received encrypted data and we need to decrypt it first
        encrypted_data = request.get_json()
        try:
            request_data = bni_utility.decrypt(BNI_ECOLLECTION_CONFIG["CREDIT_CLIENT_ID"],
                                               BNI_ECOLLECTION_CONFIG["CREDIT_SECRET_KEY"],
                                               encrypted_data["data"])
        except DecryptError:
            raise InvalidCallbackError
        #end try
        try:
            result = CallbackSchema(strict=True).validate(request_data)
        except ValidationError as error:
            raise SerializeError(error.messages)
        #end if

        # add payment channel key here to know where the request coming from
        request_data["payment_channel_key"] = "BNI_VA"
        response = CallbackServices(request_data["virtual_account"],
                                    request_data["trx_id"]).deposit(request_data)
        return response
    #end def
#end class

@api.route('/bni_va/withdraw')
class WithdrawCallback(Resource):
    """ Class where we routes Withdraw Callback Request"""
    def post(self):
        """ function that handle post request from withdraw callback url"""
        # we received encrypted data and we need to decrypt it first
        encrypted_data = request.get_json()
        try:
            request_data = bni_utility.decrypt(BNI_ECOLLECTION_CONFIG["DEBIT_CLIENT_ID"],
                                               BNI_ECOLLECTION_CONFIG["DEBIT_SECRET_KEY"],
                                               encrypted_data["data"])
        except DecryptError:
            raise InvalidCallbackError
        #end try
        try:
            result = CallbackSchema(strict=True).validate(request_data)
        except ValidationError as error:
            raise SerializeError(error.messages)
        #end if

        # add payment channel key here to know where the request coming from
        request_data["payment_channel_key"] = "BNI_VA"
        response = CallbackServices(request_data["virtual_account"],
                                    request_data["trx_id"]).withdraw(request_data)
        return response
    #end def
#end class
