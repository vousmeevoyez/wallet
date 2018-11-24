import traceback
from datetime import datetime, timedelta

from flask          import request, jsonify
from sqlalchemy.exc import IntegrityError

from app            import db
from app.callback   import bp
from app.models     import Wallet, Transaction, VirtualAccount
from app.serializer import WalletSchema, TransactionSchema, VirtualAccountSchema
from app.errors     import bad_request, internal_error, request_not_found
from app.config     import config
from app.bank       import helper as bank_helper

ACCESS_KEY_CONFIG = config.Config.ACCESS_KEY_CONFIG
VA_TYPE           = config.Config.VA_TYPE_CONFIG
TRANSACTION_NOTES = config.Config.TRANSACTION_NOTES
RESPONSE_MSG      = config.Config.RESPONSE_MSG
WALLET_CONFIG     = config.Config.WALLET_CONFIG

class CallbackController:

    def __init__(self):
        pass
    #end def

    def deposit(self, params):
        response = {
            "status_code"    : 0,
            "status_message" : "SUCCESS",
            "data"           : "NONE"
        }

        va            = params["virtual_account"]
        customer_name = params["customer_name"  ]
        trx_id        = params["trx_id"         ]
        payment_amount= params["payment_amount" ]

        virtual_account = VirtualAccount.query.filter_by(id=va, trx_id=trx_id).first()
        if virtual_account == None:
            return request_not_found()
        #end if

        # prepare inject the balance here
        deposit_payload = {
            "id"     : virtual_account.wallet_id,
            "amount" : payment_amount
        }

        deposit_response = self._inject(deposit_payload)
        if deposit_response["status"] != "SUCCESS":
            return bad_request()
        #end if

        # after successfully inject the balance we need to update the VA and empty the balance
        va_payload = {
            "trx_id"           : str(virtual_account.trx_id),
            "amount"           : "0", # set to zero
            "customer_name"    : virtual_account.name, # set to zero
            "datetime_expired" : virtual_account.datetime_expired, # set to zero
        }
        va_response = bank_helper.EcollectionHelper().update_va(va_payload)
        if va_response["status"] != "SUCCESS":
            return bad_request(RESPONSE_MSG["VA_UPDATE_FAILED"])
        #end if

        return response
    #end def

    def _inject(self, params):
        response = {
            "status" : "SUCCESS",
            "data"   : "NONE"
        }

        try:
            # parse request data 
            wallet_id  = params["id"]
            amount     = float(params["amount"])

            if amount < 0:
                response["status"] = "FAILED"
                response["data"  ] = "Invalid Amount"
                return response
            #end if

            wallet = Wallet.query.filter_by(id=wallet_id).first()
            if wallet == None:
                response["status"] = "FAILED"
                response["data"  ] = "Wallet not found"
                return response
            #end if

            if wallet.is_unlocked() == False:
                response["status"] = "FAILED"
                response["data"  ] = "Wallet is locked"
                return response
            #end if

            try:
                # credit (+) we increase balance 
                credit_transaction = Transaction(
                    source_id=wallet.id,
                    destination_id=wallet.id,
                    amount=amount,
                    transaction_type=WALLET_CONFIG["CREDIT_FLAG"],
                    transfer_type=WALLET_CONFIG["BANK_TO_VA"],
                    notes=TRANSACTION_NOTES["DEPOSIT"].format(str(amount))
                )
                credit_transaction.generate_trx_id()
                wallet.add_balance(amount)
                db.session.add(credit_transaction)

                db.session.commit()
            except:
                db.session.rollback()
                print(traceback.format_exc())
                return internal_error()

            success_message = RESPONSE_MSG["SUCCESS_DEPOSIT"].format(str(amount), wallet_id)
            response["data"] = success_message

        except Exception as e:
            response["status"] = "FAILED"
            response["data"  ] = str(e)

        return response
    #end def

#end class
