from flask          import request, jsonify

from app            import db
from app.top_up     import bp
from app.bank       import handler as bank_handler
from app.models     import Wallet, Transaction, VirtualAccount
from app.serializer import WalletSchema, TransactionSchema, VirtualAccountSchema
from app.errors     import bad_request, internal_error, request_not_found
from app.config     import config

from sqlalchemy.exc import IntegrityError
import traceback

from datetime import datetime, timedelta

ACCESS_KEY_CONFIG = config.Config.ACCESS_KEY_CONFIG
WALLET_CONFIG     = config.Config.WALLET_CONFIG
TRANSACTION_NOTES = config.Config.TRANSACTION_NOTES
RESPONSE_MSG      = config.Config.RESPONSE_MSG

@bp.route('/request', methods=["POST"])
def request_topup():
    response = { "status_code" : 0, "status_message" : "SUCCESS", "data" : "NONE" }

    try:
        # parse request data 
        request_data = request.form
        wallet_id = request_data["wallet_id"]
        pin       = request_data["pin"      ]

        data = {
            "wallet_id" : wallet_id,
            "pin"       : pin,
        }

        wallet = Wallet.query.filter_by(id=wallet_id).first()
        if wallet == None:
            return request_not_found(RESPONSE_MSG["WALLET_NOT_FOUND"].format(wallet_id))

        # checking pin
        if wallet.check_pin(pin) != True:
            return bad_request(RESPONSE_MSG["INCORRECT_PIN"])
        #end if

        # checking VA status
        if wallet.virtual_account.status != False:
            return bad_request(RESPONSE_MSG["ALREADY_REQUESTED_ERROR"])
        #end if

        # fetch VA Information 
        va_information   = VirtualAccountSchema().dump(wallet.virtual_account).data
        # generate expires time
        datetime_expired = datetime.now() + timedelta(minutes=WALLET_CONFIG["VA_TIMEOUT"])
        expires_in       = datetime_expired.timestamp()

        # modify msisdn so match BNI format
        customer_phone = wallet.msisdn[1:]
        fixed = "62"
        customer_phone = fixed + customer_phone

        va_payload = {
            "trx_id"           : str(va_information["trx_id"]),
            "amount"           : "0",
            "customer_name"    : wallet.name,
            "customer_phone"   : customer_phone,
            "virtual_account"  : str(va_information["id"]),
            "datetime_expired" : datetime_expired.strftime("%Y-%m-%d %H:%M:%S"),
        }
        print(va_payload)

        # request create VA
        result = bank_handler.Handlers().create_va("CREDIT", va_payload)
        print(result)

        if result["status"] != "SUCCESS":
            return bad_request(RESPONSE_MSG["TOPUP_ERROR"])
        #end if

        # update va information 
        va = VirtualAccount.query.filter_by(id=va_information["id"]).first()
        va.set_status(True)
        # lock wallet for incoming transaction
        wallet.lock()
        db.session.commit()

        response["data"] = { "message" : RESPONSE_MSG["SUCCESS_TOPUP"], "expires_in" : expires_in }
    except Exception as e:
        print(traceback.format_exc())
        print(str(e))
        return internal_error()
    #end try

    return jsonify(response)
#end def


@bp.route('/callback', methods=["POST"])
def topup_callback():
    response = { "status_code" : 0, "status_message" : "SUCCESS", "data" : "NONE" }

    try:
        # parse request data 
        request_data = request.form
        print(request_data)
    except Exception as e:
        print(traceback.format_exc())
        print(str(e))
        return internal_error()
    #end try

    return jsonify(response)
#end def


