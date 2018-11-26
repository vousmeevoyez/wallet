import traceback
from datetime import datetime, timedelta

from flask          import request, jsonify
from sqlalchemy.exc import IntegrityError

from app            import db
from app.wallet     import bp
from app.wallet     import helper
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

class WalletController:

    def __init__(self):
        pass
    #end def

    def create(self, params):
        response = {
            "status_code"    : 0,
            "status_message" : "SUCCESS",
            "data"           : "NONE"
        }

        wallet_creation_resp = helper.WalletHelper().generate_wallet(params)
        if wallet_creation_resp["status"] != "SUCCESS":
            return bad_request(wallet_creation_resp["data"])
        #end if

        response["data"] = wallet_creation_resp["data"]

        return response
    #end def

    def list(self, params=None):
        response = {
            "status_code"    : 0,
            "status_message" : "SUCCESS",
            "data"           : "NONE"
        }

        try:
            user_id = int(params["user_id"])

            wallet = Wallet.query.filter_by(user_id=user_id)

            response["data"] = WalletSchema(many=True).dump(wallet).data
        except Exception as e:
            print(str(e))
            print(traceback.format_exc())
            return internal_error()
        #end try

        return response
    #end def

    def details(self, params):
        response = {
            "status_code"    : 0,
            "status_message" : "SUCCESS",
            "data"           : "NONE"
        }

        try:
            wallet_id  = params["id" ]
            pin        = params["pin"]

            wallet = Wallet.query.filter_by(id=wallet_id).first()
            if wallet == None:
                return request_not_found()
            #end if

            if wallet.check_pin(pin) != True:
                return bad_request(RESPONSE_MSG["INCORRECT_PIN"])
            #end if

            wallet_information = WalletSchema().dump(wallet).data
            va_information     = VirtualAccountSchema(many=True).dump(wallet.virtual_accounts).data

            response["data"] = {
                "wallet" : wallet_information,
                "virtual_account" : va_information
            }

        except Exception as e:
            print(str(e))
            return internal_error()

        return response
    #end def

    def remove(self, params):
        response = {
            "status_code"    : 0,
            "status_message" : "SUCCESS",
            "data"           : "NONE"
        }

        try:
            wallet_id = params["id"]

            wallet = Wallet.query.filter_by(id=wallet_id).first()
            if wallet == None:
                return request_not_found()
            #end if

            #cannot delete wallet if this the only wallet
            user_id = wallet.user_id
            wallet_number = Wallet.query.filter_by(user_id=user_id).count()
            if wallet_number <= 1:
                return bad_request(RESPONSE_MSG["WALLET_REMOVAL_FAILED"])
            #end if

            # deactivating VA
            va_info = wallet.virtual_accounts
            datetime_expired = datetime.now() - timedelta(hours=WALLET_CONFIG["CREDIT_VA_TIMEOUT"])

            va_payload = {
                "trx_id"           : va_info[0].trx_id,
                "amount"           : "0",
                "customer_name"    : "NONE",
                "datetime_expired" : datetime_expired
            }
            va_response = bank_helper.EcollectionHelper().update_va(va_payload)


            db.session.delete(wallet)
            db.session.commit()
            response["data"] = RESPONSE_MSG["WALLET_REMOVED"]

        except Exception as e:
            print(str(e))
            return internal_error()

        return response
    #end def

    def check_balance(self, params):
        response = {
            "status_code"    : 0,
            "status_message" : "SUCCESS",
            "data"           : "NONE"
        }

        try:
            wallet_id  = params["id" ]
            pin        = params["pin"]

            wallet = Wallet.query.filter_by(id=wallet_id).first()
            if wallet == None:
                return request_not_found()

            if wallet.check_pin(pin) != True:
                return bad_request(RESPONSE_MSG["INCORRECT_PIN"])

            response["data"] = {
                "id" : wallet_id,
                "balance" : wallet.balance
            }

        except Exception as e:
            print(traceback.format_exc())
            print(str(e))
            return internal_error()

        return response
    #end def

    def deposit(self, params):
        response = {
            "status_code"    : 0,
            "status_message" : "SUCCESS",
            "data"           : "NONE"
        }

        try:
            # parse request data 
            wallet_id  = params["id"]
            amount     = float(params["amount"])

            if amount < 0:
                return bad_request("Invalid Amount")
            #end if

            wallet = Wallet.query.filter_by(id=wallet_id).first()
            if wallet == None:
                return request_not_found()
            #end if

            if wallet.is_unlocked() == False:
                return bad_request(RESPONSE_MSG["TRANSACTION_LOCKED"])
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
            print(str(e))
            return internal_error()

        return response
    #end def

    def history(self, wallet_id):
        response = {
            "status_code"    : 0,
            "status_message" : "SUCCESS",
            "data" : "NONE"
        }

        try:
            wallet = Wallet.query.filter_by(id=wallet_id).first()
            if wallet == None:
                return request_not_found()
            #end if

            wallet_response = Transaction.query.filter_by(source_id=wallet.id)

            response["data"] = TransactionSchema(many=True).dump(wallet_response).data

        except Exception as e:
            print(str(e))
            return internal_error()

        return response
    #end def

#end class
