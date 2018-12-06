import traceback
import sys

from flask_restplus     import Resource
from datetime import datetime

from app.api.callback           import api
from app.api.serializer         import CallbackSchema
from app.api.errors             import bad_request, internal_error, request_not_found
from app.api.config             import config
from app.api.callback.modules   import callback
from app.api.bank.utility       import remote_call

RESPONSE_MSG = config.Config.RESPONSE_MSG
BNI_ECOLLECTION_CONFIG = config.Config.BNI_ECOLLECTION_CONFIG

@api.route('/deposit')
class CallbackDeposit(Resource):
    def post(self):
        # response that only accepted by BNI
        response = {
            "status" : "000"
        }

        # we received encrypted data and we need to decrypt it first
        encrypted_data = request.get_json()
        request_data = remote_call.decrypt( BNI_ECOLLECTION_CONFIG["CREDIT_CLIENT_ID"], BNI_ECOLLECTION_CONFIG["CREDIT_SECRET_KEY"], encrypted_data["data"])

        try:
            data = {
                "virtual_account"           : int(request_data["virtual_account"]),
                "customer_name"             : request_data["customer_name"  ],
                "trx_id"                    : int(request_data["trx_id"     ]),
                "trx_amount"                : float(request_data["trx_amount" ]),
                "payment_amount"            : int(request_data["payment_amount"]),
                "cumulative_payment_amount" : int(request_data["cumulative_payment_amount"]),
                "payment_ntb"               : int(request_data["payment_ntb"]),
                "datetime_payment"          : request_data["datetime_payment"],
            }
        except:
            response["status"] = "400"
            response["data"  ] = "Invalid Request Data"
            return response
        #end try

        errors = CallbackSchema().validate(data)
        if errors:
            response["status"] = "400"
            response["data"  ] = errors
            return response
        #end if

        deposit_response = callback.CallbackController().deposit(data)
        if deposit_response["status_code"] != 0:
            response["status"] = str(deposit_response["status_code"])
        return response
    #end def
#end class

@api.route('/withdraw')
class CallbackWithdraw(Resource):
    def post(self):
        # response that only accepted by BNI
        response = {
            "status" : "000"
        }

        # we received encrypted data and we need to decrypt it first
        encrypted_data = request.get_json()
        request_data = remote_call.decrypt( BNI_ECOLLECTION_CONFIG["DEBIT_CLIENT_ID"], BNI_ECOLLECTION_CONFIG["DEBIT_SECRET_KEY"], encrypted_data["data"])

        try:
            data = {
                "virtual_account"           : int(request_data["virtual_account"]),
                "customer_name"             : request_data["customer_name"  ],
                "trx_id"                    : int(request_data["trx_id"     ]),
                "trx_amount"                : float(request_data["trx_amount" ]),
                "payment_amount"            : int(request_data["payment_amount"]),
                "cumulative_payment_amount" : int(request_data["cumulative_payment_amount"]),
                "payment_ntb"               : int(request_data["payment_ntb"]),
                "datetime_payment"          : request_data["datetime_payment"],
            }
        except:
            response["status"] = "400"
            response["data"  ] = "Invalid Request Data"
            return response
        #end try

        errors = CallbackSchema().validate(data)
        if errors:
            response["status"] = "400"
            response["data"  ] = errors
            return response
        #end if

        withdraw_response = callback.CallbackController().withdraw(data)
        if withdraw_response["status_code"] != 0:
            response["status"] = str(withdraw_response["status_code"])

        return response
    #end def
#end class
