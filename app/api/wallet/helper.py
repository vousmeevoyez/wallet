""" 
    Wallet Helper
    _________________
    this is module that help wallet creation
"""
import traceback

from flask          import request, jsonify
from sqlalchemy.exc import IntegrityError

from app.api            import db
from app.api.bank.handler import BankHandler
from app.api.serializer import WalletSchema
from app.api.http_response     import bad_request, internal_error, request_not_found
from app.config     import config

RESPONSE_MSG = config.Config.RESPONSE_MSG

class WalletHelper:
    """ Wallet Helper Class"""

    def generate_wallet(self, params, session=None):
        """
            generate wallet record and attach a virtual account to it
            args:
                params -- name, msisdn, user_id, pin
                session -- database session (optional)
        """
        # request data validator
        wallet, errors = WalletSchema().load({
            "user_id" : params["user_id"],
            "pin"     : params["pin"]
        })

        if errors:
            # should raise wallet not valid
            pass
        #end if

        if session is None:
            #session = db.session(autocommit=True)
            session = db.session
        #end if
        session.begin(subtransactions=True)

        try:
            wallet_id = wallet.generate_wallet_id()
            wallet.set_pin(params["pin"])

            session.add(wallet)

            va_payload = {
                "wallet_id" : wallet_id,
                "amount"    : 0,
                "name"      : params["name"],
                "msisdn"    : params["msisdn"],
                "type"      : "CREDIT",
            }

            # request create VA
            result = BankHandler("BNI").dispatch("CREATE_VA", va_payload)
            if result["status"] != "SUCCESS":
                session.rollback()
                response["status"] = "FAILED"
                response["data"] = RESPONSE_MSG["FAILED"]["VA_CREATION"]
                return response
            #end if

            session.commit()

        except IntegrityError as err:
            session.rollback()
        #end try
        return wallet_id
    #end def
#end class
