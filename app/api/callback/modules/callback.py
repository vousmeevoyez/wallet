import traceback
from datetime import datetime, timedelta

from flask          import request, jsonify
from sqlalchemy.exc import IntegrityError

from app.api            import db
from app.api.models     import Wallet, Transaction, VirtualAccount, ExternalLog
from app.api.serializer import WalletSchema, TransactionSchema, VirtualAccountSchema
from app.api.errors     import bad_request, internal_error, request_not_found
from app.api.config     import config
from app.api.bank       import helper as bank_helper

ACCESS_KEY_CONFIG = config.Config.ACCESS_KEY_CONFIG
TRANSACTION_NOTES = config.Config.TRANSACTION_NOTES
RESPONSE_MSG      = config.Config.RESPONSE_MSG
WALLET_CONFIG     = config.Config.WALLET_CONFIG
LOGGING_CONFIG    = config.Config.LOGGING_CONFIG

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

        va               = params["virtual_account"]
        customer_name    = params["customer_name"  ]
        trx_id           = params["trx_id"         ]
        payment_amount   = params["payment_amount" ]
        reference_number = params["payment_ntb"    ]

        # log ingoing request
        API_NAME = "DEPOSIT_NOTIFICATION"
        log = ExternalLog(request=params,
                          resource=LOGGING_CONFIG["BNI_ECOLLECTION"],
                          api_name=API_NAME,
                          api_type=LOGGING_CONFIG["INGOING"]
                         )

        virtual_account = VirtualAccount.query.filter_by(id=va, trx_id=trx_id).first()
        if virtual_account == None:
            return request_not_found()
        #end if

        # prepare inject the balance here
        deposit_payload = {
            "va_id"            : virtual_account.id,
            "reference_number" : reference_number,
            "id"               : virtual_account.wallet_id,
            "amount"           : payment_amount
        }

        deposit_response = self._inject(deposit_payload)
        log.save_response(deposit_response) # log the response here
        if deposit_response["status"] != "SUCCESS":
            log.set_status(False) # False it means failed
            return bad_request()
        #end if

        # commit log here
        log.set_status(True)
        db.session.add(log)
        db.session.commit()

        return response
    #end def

    def withdraw(self, params):
        response = {
            "status_code"    : 0,
            "status_message" : "SUCCESS",
            "data"           : "NONE"
        }

        va               = params["virtual_account" ]
        customer_name    = params["customer_name"   ]
        trx_id           = params["trx_id"          ]
        payment_amount   = params["payment_amount"  ]
        reference_number = params["payment_ntb"     ]

        # log ingoing request
        API_NAME = "WITHDRAW_NOTIFICATION"
        log = ExternalLog( request=params,
                          resource=LOGGING_CONFIG["BNI_ECOLLECTION"],
                          api_name=API_NAME,
                          api_type=LOGGING_CONFIG["INGOING"]
                         )

        virtual_account = VirtualAccount.query.filter_by(id=va, trx_id=trx_id).first()
        if virtual_account == None:
            return request_not_found()
        #end if

        # prepare deduct the balance here
        withdraw_payload = {
            "va_id"            : virtual_account.id,
            "reference_number" : reference_number,
            "id"               : virtual_account.wallet_id,
            "amount"           : payment_amount
        }

        withdraw_response = self._deduct(withdraw_payload)
        log.save_response(withdraw_response) # log the response here
        if withdraw_response["status"] != "SUCCESS":
            log.set_status(False) # False it means failed
            return bad_request()
        #end if

        # commit log here
        log.set_status(True)
        db.session.add(log)
        db.session.commit()

        return response
    #end def

    def _inject(self, params):
        response = {
            "status" : "SUCCESS",
            "data"   : "NONE"
        }

        try:
            # parse request data 
            va_id            = params["va_id"]
            reference_number = params["reference_number"]
            wallet_id        = params["id"]
            amount           = float(params["amount"])

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
                    notes=TRANSACTION_NOTES["DEPOSIT"].format(str(amount), str(va_id), str(reference_number))
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

    def _deduct(self, params):
        response = {
            "status" : "SUCCESS",
            "data"   : "NONE"
        }

        try:

            # parse request data 
            va_id            = params["va_id"]
            reference_number = params["reference_number"]
            wallet_id        = params["id"]
            amount           = float(params["amount"])

            if amount > 0:
                response["status"] = "FAILED"
                response["data"  ] = "Invalid Amount"
                return response
            #end if
            amount = abs(amount)

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

            if float(amount) > float(wallet.balance) :
                response["status"] = "FAILED"
                response["data"  ] = RESPONSE_MSG["INSUFFICIENT_BALANCE"]
                return response
            #end if

            try:
                # debit (-) we increase balance 
                debit_transaction = Transaction(
                    source_id=wallet.id,
                    destination_id=wallet.id,
                    amount=amount,
                    transaction_type=WALLET_CONFIG["DEBIT_FLAG"],
                    transfer_type=WALLET_CONFIG["VA_TO_BANK"],
                    notes=TRANSACTION_NOTES["WITHDRAW_NOTIF"].format(str(amount), str(va_id), str(reference_number))
                )
                debit_transaction.generate_trx_id()
                wallet.deduct_balance(amount)
                db.session.add(debit_transaction)

                db.session.commit()
            except:
                db.session.rollback()
                print(traceback.format_exc())
                return internal_error()

            success_message = RESPONSE_MSG["SUCCESS_WITHDRAW"].format(str(amount), wallet_id)
            response["data"] = success_message

        except Exception as e:
            response["status"] = "FAILED"
            response["data"  ] = str(e)

        return response
    #end def

#end class
