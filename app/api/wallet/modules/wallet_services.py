"""
    Wallet Services
    ________________
    This is module that serve everything related to wallet
"""
#pylint: disable=bad-whitespace
#pylint: disable=no-self-use
import random
from datetime import datetime, timedelta

from flask          import request
from sqlalchemy.exc import IntegrityError

from app.api import db

# helper
from app.api.wallet.helper import WalletHelper
from app.api.common.helper import Sms
from app.api.common.helper import QR
from app.api.bank.handler import BankHandler

# models
from app.api.models import Wallet
from app.api.models import Transaction
from app.api.models import ForgotPin
from app.api.models import Payment

# serializer
from app.api.serializer import WalletSchema
from app.api.serializer import TransactionSchema
from app.api.serializer import VirtualAccountSchema

# http error
from app.api.errors import bad_request
from app.api.errors import internal_error
from app.api.errors import request_not_found

# exception
from app.api.common.modules.sms_services import SmsError

# configuration
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

        wallet_creation_resp = WalletHelper().generate_wallet(params)
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

        wallet_id   = params["id"]
        old_pin     = params["old_pin"]
        pin         = params["pin"]
        confirm_pin = params["confirm_pin"]

        wallet = Wallet.query.filter_by(id=wallet_id).first()
        if wallet is None:
            return request_not_found(RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])
        #end if

        # first make sure the old pin is correct
        if wallet.check_pin(old_pin) is True:
            return bad_request(RESPONSE_MSG["FAILED"]["INVALID_OLD_PIN"])
        #end if

        # second need to check pin and confirmation pin must same
        if pin != confirm_pin:
            return bad_request(RESPONSE_MSG["FAILED"]["PIN_NOT_MATCH"])
        #end if

        # third make sure the new pin is not the same with the old one
        if wallet.check_pin(pin) is True:
            return bad_request(RESPONSE_MSG["FAILED"]["OLD_PIN"])
        #end if

        # update the new pin here
        wallet.set_pin(pin)
        db.session.commit()

        response["message"] = RESPONSE_MSG["SUCCESS"]["UPDATE_PIN"]
        return response
    #end def

    def send_forgot_otp(self, wallet_id):
        """
            function to send forgot otp to user phone
            args :
                wallet_id
        """
        response = {}

        wallet = Wallet.query.filter_by(id=wallet_id).first()
        if wallet is None:
            return request_not_found(RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])
        #end if

        # first check if there are any pending otp record
        pending_otp = ForgotPin.query.filter(ForgotPin.wallet_id == wallet.id,\
                               ForgotPin.status == False,\
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
        try:
            Sms().send(msisdn, "FORGOT_PIN", otp_code)
        except SmsError:
            db.session.rollback()
            return internal_error(RESPONSE_MSG["FAILED"]["SMS_ERROR"])
        #end try

        db.session.commit()

        response["data"] = {"otp_key" : otp_key}
        response["message"] = RESPONSE_MSG["SUCCESS"]["FORGOT_OTP"].format(msisdn)
        return response
    #end def

    def verify_forgot_otp(self, params):
        """
            function to verify forgot otp to user phone
            args :
                params -- parameter
        """
        response = {}

        wallet_id = params["id"]
        otp_code  = params["otp_code"]
        otp_key   = params["otp_key"]
        pin       = params["pin"]

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
        return response
    #end def

    def get_qr(self, params):
        """
            function to return encrypted wallet qr
            args:
                params --
        """
        response = {}

        wallet_id = params["id"]

        wallet = Wallet.query.filter_by(id=wallet_id).first()
        if wallet is None:
            return request_not_found(RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])
        #end if

        # build qr payload here
        qr_data = {"wallet_id" : wallet.id}
        qr_string = QR().generate(qr_data)

        response["data"] = {
            "qr_string" : qr_string
        }
        return response
    #end def
#end class
