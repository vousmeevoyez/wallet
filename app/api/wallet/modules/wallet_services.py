"""
    Wallet Services
    ________________
    This is module that serve everything related to wallet
"""
import random
import traceback
from datetime import datetime, timedelta

from flask          import request
from sqlalchemy.exc import IntegrityError
from sqlalchemy     import func
from sqlalchemy.sql import label

from app.api            import db
from app.api.wallet     import helper
from app.api.common     import helper as common_helper
from app.api.bank.handler import BankHandler
from app.api.models     import Wallet, Transaction, ForgotPin, Payment
from app.api.serializer import WalletSchema, TransactionSchema, VirtualAccountSchema
from app.api.errors     import bad_request, internal_error, request_not_found
from app.api.config     import config

ACCESS_KEY_CONFIG = config.Config.ACCESS_KEY_CONFIG
TRANSACTION_NOTES = config.Config.TRANSACTION_NOTES
RESPONSE_MSG = config.Config.RESPONSE_MSG
WALLET_CONFIG = config.Config.WALLET_CONFIG

class WalletServices:
    """ Wallet Services Class"""

    def add(self, params):
        """
            function to add new wallet to specific user
            args :
                params -
        """
        response = {}

        wallet_creation_resp = helper.WalletHelper().generate_wallet(params)
        if wallet_creation_resp["status"] != "SUCCESS":
            return bad_request(wallet_creation_resp["data"])
        #end if

        response["data"] = wallet_creation_resp["data"]
        response["message"] = RESPONSE_MSG["SUCCESS"]["CREATE_WALLET"]
        return response
    #end def

    def show(self, params=None):
        """
            function to show all wallet
            args -- params
        """
        response = {}

        wallet = Wallet.query.all()
        response["data"] = WalletSchema(many=True).dump(wallet).data
        return response
    #end def

    def info(self, params):
        """
            function to return wallet information
            args:
                params --
        """
        response = {}

        wallet_id = params["id"]

        wallet = Wallet.query.filter_by(id=wallet_id).first()
        if wallet is None:
            return request_not_found(RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])
        #end if

        wallet_information = WalletSchema().dump(wallet).data
        va_information = VirtualAccountSchema(many=True).dump(wallet.virtual_accounts).data

        response["data"] = {
            "wallet" : wallet_information,
            "virtual_account" : va_information
        }
        return response
    #end def

    """
    def remove(self, params):
            function to remove wallet
            args :
                params --
        response = {
            "status_code"    : 0,
            "status_message" : "SUCCESS",
            "data"           : "NONE"
        }

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
        #va_response = BankHandler("BNI").update_va("CREDIT", va_payload)

        try:
            db.session.delete(wallet)
            db.session.commit()
            response["data"] = RESPONSE_MSG["WALLET_REMOVED"]
        except IntegrityError as error:
            print(str(error))
            return internal_error()
        return response
    #end def
    """

    def check_balance(self, params):
        """
            function to check wallet balance
            args:
                params -- id, pin
        """
        response = {}

        wallet_id = params["id"]
        pin = params["pin"]

        wallet = Wallet.query.filter_by(id=wallet_id).first()
        if wallet is None:
            return request_not_found(RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])
        #end if

        if wallet.check_pin(pin) is not True:
            return bad_request(RESPONSE_MSG["FAILED"]["INCORRECT_PIN"])
        #end if

        response["data"] = {
            "id" : wallet_id,
            "balance" : wallet.balance
        }
        return response
    #end def

    def history(self, params):
        """
            function to check wallet transaction history
            args :
                params -- parameter
        """
        response = {}

        wallet_id = params["wallet_id"]
        start_date = params["start_date"]
        end_date = params["end_date"]
        transaction_type = params["flag"]

        wallet = Wallet.query.filter_by(id=wallet_id).first()
        if wallet is None:
            return request_not_found()
        #end if

        conditions = [Transaction.wallet_id == wallet.id]
        # filter by transaction type
        if transaction_type == "IN":
            conditions.append(Payment.payment_type == True)
        elif transaction_type == "OUT":
            conditions.append(Payment.payment_type == False)
        #end if

        # filter by transaction date
        if start_date is not None and end_date is not None:
            start_date = datetime.strptime(start_date, "%Y/%m/%d")
            end_date = datetime.strptime(end_date, "%Y/%m/%d")
            end_date = end_date + timedelta(hours=23, minutes=59)

            conditions.append(Transaction.created_at.between(start_date, \
                                                                 end_date))
        #end if
        wallet_response = Transaction.query.join(Payment,
                                                 Transaction.payment_id == \
                                                 Payment.id,
                                                 ).filter(*conditions)
        response["data"] = TransactionSchema(many=True,
                                             exclude=["payment_details",]).\
                            dump(wallet_response).data
        return response
    #end def

    def history_details(self, wallet_id, transaction_id):
        """
            function to check wallet transaction details
            args :
                wallet_id --
                transaction_id --
        """
        response = {}

        wallet = Wallet.query.filter_by(id=wallet_id).first()
        if wallet is None:
            return request_not_found(RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])
        #end if

        history_details = Transaction.query.filter_by(wallet_id=wallet.id,\
                                                      id=transaction_id).first()
        response["data"] = TransactionSchema().dump(history_details).data
        return response
    #end def

    def update_pin(self, params):
        """ 
            function to update wallet pin
            args :
                params --
        """
        response = {}

        try:
            wallet_id = params["id"]
            pin = params["pin"]
            confirm_pin = params["confirm_pin"]

            wallet = Wallet.query.filter_by(id=wallet_id).first()
            if wallet is None:
                return request_not_found(RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])
            #end if

            # first need to check pin and confirmation pin must same
            if pin != confirm_pin:
                return bad_request(RESPONSE_MSG["FAILED"]["PIN_NOT_MATCH"])
            #end if

            # second make sure the new pin is not the same with the old one
            if wallet.check_pin(pin) is True:
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
        """
            function to send forgot otp to user phone
            args :
                wallet_id
        """
        response = {}

        try:
            wallet = Wallet.query.filter_by(id=wallet_id).first()
            if wallet is None:
                return request_not_found(RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])
            #end if

            # first check if there are any pending otp record
            pending_otp = ForgotPin.query.filter(ForgotPin.wallet_id == wallet.id,\
                                   ForgotPin.status is False,\
                                   ForgotPin.valid_until > datetime.now() \
                                ).count()
            if pending_otp > 0:
                return bad_request(RESPONSE_MSG["FAILED"]["OTP_PENDING"])
            #end if

            # second generate random verify otp number to user phone
            start_range = 1000
            end_range = 9999
            otp_code = random.randint(start_range, end_range)

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
            sms_otp_resp = common_helper.SmsHelper().send_sms(msisdn, "FORGOT_PIN", otp_code)

            if sms_otp_resp["status"] != "SUCCESS":
                db.session.rollback()
                return internal_error(sms_otp_resp["data"])
            #end if

            db.session.commit()

            response["data"] = {"otp_key" : otp_key}
            response["message"] = RESPONSE_MSG["SUCCESS"]["FORGOT_OTP"].format(msisdn)
        except Exception as e:
            print(traceback.format_exc())
            print(str(e))
            return internal_error()
        return response
    #end def

    def verify_forgot_otp(self, params):
        """
            function to verify forgot otp to user phone
            args :
                params -- parameter
        """
        response = {}

        try:
            wallet_id = params["id"]
            otp_code = params["otp_code"]
            otp_key = params["otp_key"]
            pin = params["pin"]

            wallet = Wallet.query.filter_by(id=wallet_id).first()
            if wallet is None:
                return request_not_found(RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])
            #end if

            # fetch forgot otp record
            forgot_otp = ForgotPin.query.filter_by(
                wallet_id=wallet_id,
                otp_key=otp_key
            ).first()

            if forgot_otp is None:
                return request_not_found(RESPONSE_MSG["FAILED"]["OTP_NOT_FOUND"])
            #end if

            if forgot_otp.status is not False:
                return bad_request(RESPONSE_MSG["FAILED"]["OTP_ALREADY_VERIFIED"])
            #end if

            if forgot_otp.check_otp_code(otp_code) is not True:
                return bad_request(RESPONSE_MSG["FAILED"]["INVALID_OTP_CODE"])
            #end if

            # update otp record to DONE
            forgot_otp.status = True

            # set new pin here
            wallet.set_pin(pin)
            db.session.commit()

            response["message"] = RESPONSE_MSG["SUCCESS"]["FORGOT_PIN"]
        except Exception as error:
            print(traceback.format_exc())
            print(str(error))
            return internal_error()
        return response
    #end def

#end class
