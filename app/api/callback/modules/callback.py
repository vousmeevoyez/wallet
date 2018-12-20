import traceback
from datetime import datetime, timedelta

from flask          import request, jsonify
from sqlalchemy.exc import IntegrityError, InvalidRequestError

from app.api            import db
from app.api.models     import Wallet, Transaction, VirtualAccount, ExternalLog, Payment, PaymentChannel
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

    def _create_payment(self, params, session=None):
        if session == None:
            session = db.session
        #end if
        session.begin(subtransactions=True)

        payment_channel_key = params["payment_channel_key"]
        source_account      = params["source_account"     ]
        to                  = params["to"                 ]
        ref_number          = params["reference_number"   ]
        amount              = params["payment_amount"     ]
        payment_type        = params["payment_type"       ]

        # fetch payment channel
        payment_channel = PaymentChannel.query.filter_by(key=payment_channel_key).first()

        # build payment object
        payment = Payment(
            source_account=source_account,
            to=to,
            ref_number=ref_number,
            amount=amount,
            channel_id=payment_channel.id,
            payment_type=payment_type,
        )
        session.add(payment)
        session.flush()

        return payment.id
    #end def

    def deposit(self, params):
        response = {
            "status_code"    : 0,
            "status_message" : "SUCCESS",
            "data"           : "NONE"
        }

        va                  = params["virtual_account"    ]
        trx_id              = params["trx_id"             ]
        payment_amount      = params["payment_amount"     ]
        reference_number    = params["payment_ntb"        ]
        payment_channel_key = params["payment_channel_key"]

        # CREATE TRANSACTION SESSION
        try:
            session = db.session(autocommit=True)
            session.begin(subtransactions=True)
        except InvalidRequestError:
            db.session.commit()
            session = db.session()
        #end try

        # log ingoing request
        API_NAME = "DEPOSIT_NOTIFICATION"
        log = ExternalLog(request=params,
                          resource=LOGGING_CONFIG["BNI_ECOLLECTION"],
                          api_name=API_NAME,
                          api_type=LOGGING_CONFIG["INGOING"]
                         )

        virtual_account = VirtualAccount.query.filter_by(id=va, trx_id=trx_id).first()
        if virtual_account == None:
            response["status_code"] = "404"
            response["data"       ] = RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"]
            return response
        #end if

        # create payment
        payment_payload = {
            "payment_channel_key" : payment_channel_key,
            "source_account"      : virtual_account.id,
            "to"                  : virtual_account.wallet_id,
            "reference_number"    : reference_number,
            "payment_amount"      : payment_amount,
            "payment_type"        : True # Credit
        }
        payment_id = self._create_payment(payment_payload, session)

        # prepare inject the balance here
        deposit_payload = {
            "payment_id" : payment_id,
            "wallet_id"  : virtual_account.wallet_id,
            "amount"     : payment_amount
        }

        deposit_response = self._inject(deposit_payload, session)
        log.save_response(deposit_response) # log the response here
        if deposit_response["status"] != "SUCCESS":
            log.set_status(False) # False it means failed
            response["status_code"] = "400"
            response["data"       ] = RESPONSE_MSG["FAILED"]["INJECT"]
            return response
        #end if

        # commit log here
        log.set_status(True)
        session.add(log)
        session.commit()

        return response
    #end def

    def withdraw(self, params):
        response = {
            "status_code"    : 0,
            "status_message" : "SUCCESS",
            "data"           : "NONE"
        }

        va                  = params["virtual_account"    ]
        trx_id              = params["trx_id"             ]
        payment_amount      = params["payment_amount"     ]
        reference_number    = params["payment_ntb"        ]
        payment_channel_key = params["payment_channel_key"]

        # CREATE TRANSACTION SESSION
        try:
            session = db.session(autocommit=True)
            session.begin(subtransactions=True)
        except InvalidRequestError:
            db.session.commit()
            session = db.session()
        #end try

        # log ingoing request
        API_NAME = "WITHDRAW_NOTIFICATION"
        log = ExternalLog( request=params,
                          resource=LOGGING_CONFIG["BNI_ECOLLECTION"],
                          api_name=API_NAME,
                          api_type=LOGGING_CONFIG["INGOING"]
                         )

        virtual_account = VirtualAccount.query.filter_by(id=va, trx_id=trx_id).first()
        if virtual_account == None:
            response["status_code"] = "404"
            response["data"       ] = RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"]
            return response
        #end if

        # create payment
        payment_payload = {
            "payment_channel_key" : payment_channel_key,
            "source_account"      : virtual_account.id,
            "to"                  : virtual_account.wallet_id,
            "reference_number"    : reference_number,
            "payment_amount"      : payment_amount,
            "payment_type"        : False # debit
        }
        payment_id = self._create_payment(payment_payload, session)

        # prepare deduct the balance here
        withdraw_payload = {
            "payment_id" : payment_id,
            "wallet_id"  : virtual_account.wallet_id,
            "amount"     : payment_amount
        }

        withdraw_response = self._deduct(withdraw_payload)
        log.save_response(withdraw_response) # log the response here
        if withdraw_response["status"] != "SUCCESS":
            log.set_status(False) # False it means failed
            response["status_code"] = "400"
            response["data"       ] = RESPONSE_MSG["FAILED"]["DEDUCT"]
            return response
        #end if

        # commit log here
        log.set_status(True)
        db.session.add(log)
        db.session.commit()

        return response
    #end def

    def _inject(self, params, session=None):
        response = {
            "status" : "SUCCESS",
            "data"   : "NONE"
        }

        if session == None:
            session = db.session
        #end if
        session.begin(subtransactions=True)

        # parse request data 
        payment_id  = params["payment_id"]
        wallet_id   = params["wallet_id"]
        amount      = float(params["amount"])

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
                payment_id=payment_id,
                wallet_id=wallet.id,
                amount=amount,
                transaction_type=WALLET_CONFIG["DEPOSIT"],
                notes=TRANSACTION_NOTES["DEPOSIT"].format(str(amount))
            )
            credit_transaction.current_balance("ADD", amount)
            credit_transaction.generate_trx_id()

            wallet.add_balance(amount)
            session.add(credit_transaction)

            session.commit()
        except:
            session.rollback()
            print(traceback.format_exc())
            return internal_error()
        #end try

        success_message = RESPONSE_MSG["SUCCESS"]["DEPOSIT"].format(str(amount), wallet_id)
        response["data"] = success_message
        return response
    #end def

    def _deduct(self, params, session=None):
        response = {
            "status" : "SUCCESS",
            "data"   : "NONE"
        }

        if session == None:
            session = db.session
        #end if
        session.begin(subtransactions=True)

        # parse request data 
        payment_id  = params["payment_id"]
        wallet_id   = params["wallet_id"]
        amount      = float(params["amount"])

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
            response["data"  ] = RESPONSE_MSG["FAILED"]["INSUFFICIENT_BALANCE"]
            return response
        #end if

        try:
            # debit (-) we increase balance 
            debit_transaction = Transaction(
                payment_id=payment_id,
                wallet_id=wallet.id,
                amount=amount,
                transaction_type=WALLET_CONFIG["WITHDRAW"],
                notes=TRANSACTION_NOTES["WITHDRAW_NOTIF"].format(str(amount))
            )
            debit_transaction.current_balance("DEDUCT", amount)
            debit_transaction.generate_trx_id()

            wallet.deduct_balance(amount)
            session.add(debit_transaction)

            session.commit()
        except:
            session.rollback()
            print(traceback.format_exc())
            return internal_error()

        success_message = RESPONSE_MSG["SUCCESS"]["WITHDRAW"].format(str(amount), wallet_id)
        response["data"] = success_message
        return response
    #end def
#end class
