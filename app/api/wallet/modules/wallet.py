import random
import traceback
from datetime import datetime, timedelta

from flask          import request
from sqlalchemy.exc import IntegrityError

from app.api            import db
from app.api.wallet     import helper
from app.api.common     import helper as common_helper
from app.api.bank       import helper as bank_helper
from app.api.models     import Wallet, Transaction, VirtualAccount, ForgotPin
from app.api.serializer import WalletSchema, TransactionSchema, VirtualAccountSchema
from app.api.errors     import bad_request, internal_error, request_not_found
from app.api.config     import config

ACCESS_KEY_CONFIG = config.Config.ACCESS_KEY_CONFIG
TRANSACTION_NOTES = config.Config.TRANSACTION_NOTES
RESPONSE_MSG      = config.Config.RESPONSE_MSG
WALLET_CONFIG     = config.Config.WALLET_CONFIG

class WalletController:

    def __init__(self):
        pass
    #end def

    def create(self, params):
        response = {}

        wallet_creation_resp = helper.WalletHelper().generate_wallet(params)
        if wallet_creation_resp["status"] != "SUCCESS":
            return bad_request(wallet_creation_resp["data"])
        #end if

        response["data"] = wallet_creation_resp["data"]
        response["message"] = RESPONSE_MSG["SUCCESS"]["CREATE_WALLET"]
        return response
    #end def

    def all(self, params=None):
        response = {}

        try:
            wallet = Wallet.query.all()
            response["data"] = WalletSchema(many=True).dump(wallet).data
        except Exception as e:
            print(str(e))
            print(traceback.format_exc())
            return internal_error()
        #end try

        return response
    #end def

    def details(self, params):
        response = {}

        try:
            wallet_id  = params["id" ]

            wallet = Wallet.query.filter_by(id=wallet_id).first()
            if wallet == None:
                return request_not_found(RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])
            #end if

            wallet_information = WalletSchema().dump(wallet).data
            va_information     = VirtualAccountSchema(many=True).dump(wallet.virtual_accounts).data

            response["data"] = {
                "wallet" : wallet_information,
                "virtual_account" : va_information
            }

        except Exception as e:
            print(traceback.format_exc())
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
            va_response = bank_helper.EcollectionHelper().update_va("CREDIT", va_payload)

            db.session.delete(wallet)
            db.session.commit()
            response["data"] = RESPONSE_MSG["WALLET_REMOVED"]

        except Exception as e:
            print(str(e))
            return internal_error()

        return response
    #end def

    def check_balance(self, params):
        response = {}

        try:
            wallet_id  = params["id" ]
            pin        = params["pin"]

            wallet = Wallet.query.filter_by(id=wallet_id).first()
            if wallet == None:
                return request_not_found(RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])
            #end if

            if wallet.check_pin(pin) != True:
                return bad_request(RESPONSE_MSG["FAILED"]["INCORRECT_PIN"])
            #end if

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

    def history(self, wallet_id):
        response = {}

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

    def update_pin(self, params):
        response = {}

        try:
            wallet_id   = params["id"]
            pin         = params["pin"]
            confirm_pin = params["confirm_pin"]

            wallet = Wallet.query.filter_by(id=wallet_id).first()
            if wallet == None:
                return request_not_found(RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])
            #end if

            # first need to check pin and confirmation pin must same
            if pin != confirm_pin:
                return bad_request(RESPONSE_MSG["FAILED"]["PIN_NOT_MATCH"])
            #end if

            # second make sure the new pin is not the same with the old one
            if wallet.check_pin(pin) == True:
                return bad_request(RESPONSE_MSG["FAILED"]["OLD_PIN"])
            #end if

            # update the new pin here
            wallet.set_pin(pin)
            db.session.commit()

            response["message"] = RESPONSE_MSG["SUCCESS"]["UPDATE_PIN"]
        except Exception as e:
            print(str(e))
            return internal_error()

        return response
    #end def

    def send_forgot_otp(self, wallet_id):
        response = {}

        try:
            wallet = Wallet.query.filter_by(id=wallet_id).first()
            if wallet == None:
                return request_not_found(RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])
            #end if

            # first check if there are any pending otp record
            pending_otp = ForgotPin.query.filter(ForgotPin.wallet_id==wallet.id, ForgotPin.status==False, ForgotPin.valid_until > datetime.now()).count()
            if pending_otp != 0:
                return request_not_found(RESPONSE_MSG["FAILED"]["OTP_PENDING"])
            #end if

            # second generate random verify otp number to user phone
            START_RANGE = 1000
            END_RANGE   = 9999
            otp_code = random.randint(START_RANGE, END_RANGE)

            # third add record to database contain hashed otp code
            valid_until = datetime.now() + timedelta(minutes=WALLET_CONFIG["OTP_TIMEOUT"])
            forgot_pin = ForgotPin(
                wallet_id=wallet.id,
                valid_until=valid_until,
            )
            forgot_pin.set_otp_code(str(otp_code))
            otp_key = forgot_pin.generate_otp_key()
            db.session.add(forgot_pin)

            # fourth send the forgot otp sms to user phone
            # fetch required information for sending sms here
            msisdn = str(wallet.user.phone_ext) + str(wallet.user.phone_number)
            sms_status = common_helper.SmsHelper().send_sms( msisdn, "FORGOT_PIN", otp_code)

            db.session.commit()

            response["data"   ] = { "otp_key" : otp_key }
            response["message"] = RESPONSE_MSG["SUCCESS"]["FORGOT_OTP"].format(msisdn)
        except Exception as e:
            print(traceback.format_exc())
            print(str(e))
            return internal_error()

        return response
    #end def

    def verify_forgot_otp(self, params):
        response = {}

        try:
            wallet_id = params["id"       ]
            otp_code  = params["otp_code" ]
            otp_key   = params["otp_key"  ]
            pin       = params["pin"      ]

            wallet = Wallet.query.filter_by(id=wallet_id).first()
            if wallet == None:
                return request_not_found(RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])
            #end if

            # fetch forgot otp record
            forgot_otp = ForgotPin.query.filter_by(
                wallet_id=wallet_id,
                otp_key=otp_key
            ).first()

            if forgot_otp == None:
                return request_not_found(RESPONSE_MSG["FAILED"]["OTP_NOT_FOUND"])
            #end if

            if forgot_otp.status != False:
                return bad_request(RESPONSE_MSG["FAILED"]["OTP_ALREADY_VERIFIED"])
            #end if

            if forgot_otp.check_otp_code(otp_code) != True:
                return bad_request(RESPONSE_MSG["FAILED"]["INVALID_OTP_CODE"])
            #end if

            # update otp record to DONE
            forgot_otp.status = True

            # set new pin here
            wallet.set_pin(pin)
            db.session.commit()

            response["message"] = RESPONSE_MSG["SUCCESS"]["FORGOT_PIN"]
        except Exception as e:
            print(traceback.format_exc())
            print(str(e))
            return internal_error()

        return response
    #end def

#end class
