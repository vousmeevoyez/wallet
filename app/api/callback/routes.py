"""
    Callback Routes
    ______________________
    this module that receive http request from callback url
"""
from flask_restplus     import Resource
from flask              import request

from app.api.callback           import api
from app.api.serializer         import CallbackSchema
from app.api.http_response             import bad_request, internal_error, request_not_found
from app.config             import config
from app.api.bank.bni.utility   import remote_call as bni_utility
from app.api.callback.modules.callback_services import CallbackServices

BNI_ECOLLECTION_CONFIG = config.Config.BNI_ECOLLECTION_CONFIG

@api.route('/bni_va/deposit')
class DepositCallback(Resource):
    """ Class where we routes Deposit Callback Request"""
    def post(self):
        """ Function to receive post request from deposit callback url"""
        # response that only accepted by BNI
        response = {
            "status" : "000"
        }

        # we received encrypted data and we need to decrypt it first
        encrypted_data = request.get_json()
        request_data = bni_utility.decrypt(BNI_ECOLLECTION_CONFIG["CREDIT_CLIENT_ID"],
                                           BNI_ECOLLECTION_CONFIG["CREDIT_SECRET_KEY"],
                                           encrypted_data["data"])

        try:
            data = {
                "virtual_account"           : int(request_data["virtual_account"]),
                "customer_name"             : request_data["customer_name"],
                "trx_id"                    : int(request_data["trx_id"]),
                "trx_amount"                : float(request_data["trx_amount"]),
                "payment_amount"            : int(request_data["payment_amount"]),
                "cumulative_payment_amount" : int(request_data["cumulative_payment_amount"]),
                "payment_ntb"               : int(request_data["payment_ntb"]),
                "datetime_payment"          : request_data["datetime_payment"],
            }
        except:
            response["status"] = "400"
            response["data"] = "Invalid Request Data"
            return response
        #end try

        errors = CallbackSchema().validate(data)
        if errors:
            response["status"] = "400"
            response["data"] = errors
            return response
        #end if

        # add payment channel key here to know where the request coming from
        data["payment_channel_key"] = "BNI_VA"
        deposit_response = CallbackServices().deposit(data)
        if deposit_response["status_code"] != 0:
            response["status"] = str(deposit_response["status_code"])
        return response
    #end def
#end class

@api.route('/bni_va/withdraw')
class WithdrawCallback(Resource):
    """ Class where we routes Withdraw Callback Request"""
    def post(self):
        """ function that handle post request from withdraw callback url"""
        # response that only accepted by BNI
        response = {
            "status" : "000"
        }

        # we received encrypted data and we need to decrypt it first
        encrypted_data = request.get_json()
        request_data = bni_utility.decrypt(BNI_ECOLLECTION_CONFIG["DEBIT_CLIENT_ID"],
                                           BNI_ECOLLECTION_CONFIG["DEBIT_SECRET_KEY"],
                                           encrypted_data["data"])
        try:
            data = {
                "virtual_account"           : int(request_data["virtual_account"]),
                "customer_name"             : request_data["customer_name"],
                "trx_id"                    : int(request_data["trx_id"]),
                "trx_amount"                : float(request_data["trx_amount"]),
                "payment_amount"            : int(request_data["payment_amount"]),
                "cumulative_payment_amount" : int(request_data["cumulative_payment_amount"]),
                "payment_ntb"               : int(request_data["payment_ntb"]),
                "datetime_payment"          : request_data["datetime_payment"],
            }
        except:
            response["status"] = "400"
            response["data"] = "Invalid Request Data"
            return response
        #end try

        errors = CallbackSchema().validate(data)
        if errors:
            response["status"] = "400"
            response["data"] = errors
            return response
        #end if

        # add payment channel key here to know where the request coming from
        data["payment_channel_key"] = "BNI_VA"
        withdraw_response = CallbackServices().withdraw(data)
        if withdraw_response["status_code"] != 0:
            response["status"] = str(withdraw_response["status_code"])
        #end if
        return response
    #end def
#end class
