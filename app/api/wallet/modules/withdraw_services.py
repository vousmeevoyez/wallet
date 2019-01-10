import traceback
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError

from app.api            import db
from app.api.withdraw   import bp
from app.api.bank       import helper as bank_helper
from app.api.models     import Wallet, Transaction, VirtualAccount, Withdraw
from app.api.serializer import WalletSchema, TransactionSchema, VirtualAccountSchema
from app.api.errors     import bad_request, internal_error, request_not_found
from app.api.config     import config

ACCESS_KEY_CONFIG = config.Config.ACCESS_KEY_CONFIG
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

        session = db.session

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

        # before creating a cardless va, we need to make sure there's no ongoing withdraw request
        pending_withdraw = Withdraw.query.filter(Withdraw.wallet_id==wallet.id, Withdraw.valid_until > datetime.now()).count()
        if pending_withdraw != 0:
            return bad_request(RESPONSE_MSG["FAILED"]["WITHDRAW_PENDING"])
        #end if

        # creating withdraw record and set it to valid for certain period of time
        valid_until = datetime.now() + timedelta(hours=WALLET_CONFIG["CREDIT_VA_TIMEOUT"])
        withdraw = Withdraw(
            wallet_id=wallet.id,
            valid_until=valid_until,
        )
        session.add(withdraw)

        user_info = wallet.user
        va_payload = {
            "wallet_id"        : wallet_id,
            "amount"           : int(amount),
            "customer_name"    : user_info.name,
            "customer_phone"   : user_info.msisdn,
        }

        va_response = bank_helper.EcollectionHelper().create_va("CARDLESS", va_payload, session)
        if va_response["status"] != "SUCCESS":
            session.rollback()
            return bad_request(va_response["data"])
        #end if

        session.commit()

        response["data"] = va_response["data"]
        return response
    #end def
#end class
