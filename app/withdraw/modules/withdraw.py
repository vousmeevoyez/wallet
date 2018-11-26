import traceback
from datetime import datetime, timedelta

from flask          import request, jsonify
from sqlalchemy.exc import IntegrityError

from app            import db
from app.withdraw   import bp
from app.bank       import helper as bank_helper
from app.models     import Wallet, Transaction, VirtualAccount
from app.serializer import WalletSchema, TransactionSchema, VirtualAccountSchema
from app.errors     import bad_request, internal_error, request_not_found
from app.config     import config

ACCESS_KEY_CONFIG = config.Config.ACCESS_KEY_CONFIG
VA_TYPE           = config.Config.VA_TYPE_CONFIG
TRANSACTION_NOTES = config.Config.TRANSACTION_NOTES
RESPONSE_MSG      = config.Config.RESPONSE_MSG
WALLET_CONFIG     = config.Config.WALLET_CONFIG

class WithdrawController:

    def __init__(self):
        pass
    #end def

    def request(self, params):
        response = {
            "status_code"    : 0,
            "status_message" : "SUCCESS",
            "data"           : "NONE"
        }

        wallet_id = params["wallet_id"]
        pin       = params["pin"      ]
        amount    = float(params["amount"])

        wallet = Wallet.query.filter_by(id=wallet_id).first()
        if wallet == None:
            return request_not_found()
        #end if

        if wallet.check_pin(pin) != True:
            return bad_request(RESPONSE_MSG["INCORRECT_PIN"])
        #end if

        if amount < float(WALLET_CONFIG["MINIMAL_WITHDRAW"]):
            return bad_request(RESPONSE_MSG["MIN_WITHDRAW_FAILED"].format(str(WALLET_CONFIG["MINIMAL_WITHDRAW"])))
        #end if

        if amount > float(WALLET_CONFIG["MAX_WITHDRAW"]):
            return bad_request(RESPONSE_MSG["MAX_WITHDRAW_FAILED"].format(str(WALLET_CONFIG["MAX_WITHDRAW"])))
        #end if

        if amount > float(wallet.balance):
            return bad_request(RESPONSE_MSG["INSUFFICIENT_BALANCE"])
        #end if

        user_info = wallet.user
        va_payload = {
            "wallet_id"        : wallet_id,
            "amount"           : int(wallet.balance),
            "customer_name"    : user_info.name,
            "customer_phone"   : user_info.msisdn,
        }

        va_response = bank_helper.EcollectionHelper().create_va("CARDLESS", va_payload)
        if va_response["status"] != "SUCCESS":
            return bad_request(va_response["data"])
        #end if

        response["data"] = va_response

        return response
    #end def

#end class
