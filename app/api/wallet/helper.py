import traceback
from datetime import datetime, timedelta

from flask          import request, jsonify
from sqlalchemy.exc import IntegrityError

from app.api            import db
from app.api.bank       import helper as bank_helper
from app.api.models     import Wallet, Transaction, VirtualAccount
from app.api.serializer import WalletSchema
from app.api.errors     import bad_request, internal_error, request_not_found
from app.api.config     import config

RESPONSE_MSG      = config.Config.RESPONSE_MSG

class WalletHelper(object):

    def __init__(self):
        pass
    #end def

    def generate_wallet(self, params, session=None):
        response = {
            "status" : "SUCCESS",
            "data"   : "NONE"
        }

        try:
            # parse request data 
            name       = params["name"   ]
            msisdn     = params["msisdn" ]
            user_id    = params["user_id"]
            pin        = params["pin"    ]

            data = {
                "user_id" : user_id,
                "pin"     : pin,
            }

            # request data validator
            wallet, errors = WalletSchema().load(data)
            if errors:
                response["status"] = "FAILED"
                response["data"  ] = errors
                return response
            #end if

            if session == None:
                #session = db.session(autocommit=True)
                session = db.session
            #end if
            session.begin(subtransactions=True)

            try:
                wallet_id = wallet.generate_wallet_id()
                wallet.set_pin(pin)

                session.add(wallet)

                va_payload = {
                    "wallet_id"        : wallet_id,
                    "amount"           : 0,
                    "customer_name"    : name,
                    "customer_phone"   : msisdn,
                }

                # request create VA
                result = bank_helper.EcollectionHelper().create_va("CREDIT", va_payload, session)
                if result["status"] != "SUCCESS":
                    session.rollback()
                    response["status"] = "FAILED"
                    response["data"  ] = RESPONSE_MSG["FAILED"]["VA_CREATION"]
                    return response

                session.commit()

            except IntegrityError as err:
                print(err)
                session.rollback()
                response["status"] = "FAILED"
                response["data"  ] = RESPONSE_MSG["FAILED"]["ERROR_ADDING_RECORD"]
                return response
            #end try

            response["data"] = { "wallet_id" : wallet_id }

        except Exception as e:
            print(traceback.format_exc())
            print(str(e))
            response["status"] = "FAILED"
            response["data"] = str(e)
        #end try

        return response
    #end def

#end class