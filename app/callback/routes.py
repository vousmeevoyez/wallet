import traceback
import sys
from flask              import request, jsonify

from app.callback               import bp
from app.serializer             import CallbackSchema
from app.errors                 import bad_request, internal_error, request_not_found
from app.config                 import config
from app.callback.modules       import callback
from app.bank.utility           import remote_call

RESPONSE_MSG = config.Config.RESPONSE_MSG
BNI_ECOLLECTION_CONFIG = config.Config.BNI_ECOLLECTION_CONFIG

@bp.route('/deposit', methods=["POST"])
def callback_deposit_routes():

    # we received encrypted data and we need to decrypt it first
    encrypted_data = request.get_json()
    request_data = remote_call.decrypt( BNI_ECOLLECTION_CONFIG["CLIENT_ID"], BNI_ECOLLECTION_CONFIG["SECRET_KEY"], encrypted_data["data"])

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
    except Exception as e:
        print(traceback.format_exc())
        print(str(e))
        return jsonify( bad_request("invalid request data") )
    #end try

    errors = CallbackSchema().validate(data)
    if errors:
        return jsonify(bad_request(errors))
    #end if

    response = callback.CallbackController().deposit(data)

    return jsonify(response)
#end def