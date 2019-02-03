"""
    Wallet Services
    ________________
    This is module that serve everything related to wallet
"""
#pylint: disable=bad-whitespace
#pylint: disable=no-self-use
import random
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError

from app.api import db

# helper
from app.api.wallet.helper import WalletHelper
from app.api.common.helper import Sms
from app.api.common.helper import QR

# models
from app.api.models import Wallet
from app.api.models import Transaction
from app.api.models import ForgotPin
from app.api.models import Payment

# decorator
from app.api.wallet.decorator import wallet_exist

# serializer
from app.api.serializer import WalletSchema
from app.api.serializer import TransactionSchema
from app.api.serializer import VirtualAccountSchema

# http error
from app.api.http_response import bad_request
from app.api.http_response import unprocessable_entity
from app.api.http_response import request_not_found
from app.api.http_response import created
from app.api.http_response import no_content

# exception
from app.api.common.modules.sms_services import SmsError

# configuration
from app.config import config

TRANSACTION_NOTES = config.Config.TRANSACTION_NOTES
WALLET_CONFIG = config.Config.WALLET_CONFIG
ERROR  = config.Config.ERROR_HEADER

class WalletServices:
    """ Wallet Services Class"""

    @staticmethod
    def add(params, session=None):
        """
            create wallet record
            args:
                params -- name, msisdn, user_id, pin
                session -- database session (optional)
        """
        if session is None:
            #session = db.session(autocommit=True)
            session = db.session
        #end if
        session.begin(nested=True)

        wallet = Wallet(user_id=params["user_id"])
        wallet_id = wallet.generate_wallet_id()
        wallet.set_pin(params["pin"])

        try:
            session.add(wallet)
            session.commit()
        except IntegrityError as error:
            #print(error.origin)
            session.rollback()
            return unprocessable_entity(ERROR["DUPLICATE_WALLET"])
        #end try
        response = {
            "wallet_id" : wallet_id
        }
        return created(response)
    #end def

    @staticmethod
    def show(params=None):
        """
            function to show all wallet
            args -- params
        """
        wallet = Wallet.query.all()
        response = WalletSchema(many=True).dump(wallet).data
        return response
    #end def

    @staticmethod
    @wallet_exist
    def info(self, params):
        """
            function to return wallet information
            args:
                params --
        """
        wallet_information = WalletSchema().dump(wallet).data
        va_information = VirtualAccountSchema(many=True).dump(wallet.virtual_accounts).data

        response = {
            "wallet" : wallet_information,
            "virtual_account" : va_information
        }
        return response
    #end def

    def remove(self):
        """ remove wallet but just change it to deactivate """

        if self.wallet is None:
            return request_not_found()
        #end if

        #cannot delete wallet if this the only wallet
        user_id = self.wallet.user_id
        wallet_number = Wallet.query.filter_by(user_id=user_id).count()
        if wallet_number <= 1:
            return bad_request(ERROR["ONLY_WALLET"])
        #end if

        self.wallet.status = 0 # deactive
        db.session.commit()

        return no_content()
    #end def

    def check_balance(self, params):
        """
            function to check wallet balance
            args:
                params -- id, pin
        """
        pin = params["pin"]

        if self.wallet is None:
            return request_not_found()
        #end if

        if self.wallet.check_pin(pin) is not True:
            return bad_request(ERROR["INCORRECT_PIN"])
        #end if

        response = {
            "id"      : self.wallet.id,
            "balance" : self.wallet.balance
        }
        return response
    #end def

    def history(self, params):
        """
            function to check wallet transaction history
            args :
                params -- parameter
        """
        start_date = params["start_date"]
        end_date = params["end_date"]
        transaction_type = params["flag"]

        if self.wallet is None:
            return request_not_found()
        #end if

        conditions = [Transaction.wallet_id == self.wallet.id]
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
        response = TransactionSchema(many=True,
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
        wallet = Wallet.query.filter_by(id=wallet_id).first()
        if wallet is None:
            return request_not_found()
        #end if

        history_details = Transaction.query.filter_by(wallet_id=wallet.id,\
                                                      id=transaction_id).first()
        response = TransactionSchema().dump(history_details).data
        return response
    #end def

    def update_pin(self, params):
        """
            function to update wallet pin
            args :
                params --
        """
        wallet_id   = params["id"]
        old_pin     = params["old_pin"]
        pin         = params["pin"]
        confirm_pin = params["confirm_pin"]

        wallet = Wallet.query.filter_by(id=wallet_id).first()
        if wallet is None:
            return request_not_found()
        #end if

        # first make sure the old pin is correct
        if wallet.check_pin(old_pin) is True:
            return bad_request(ERROR["INCORRECT_PIN"])
        #end if

        # second need to check pin and confirmation pin must same
        if pin != confirm_pin:
            return bad_request(ERROR["PIN_NOT_MATCH"])
        #end if

        # third make sure the new pin is not the same with the old one
        if wallet.check_pin(pin) is True:
            return bad_request(ERROR["DUPLICATE_PIN"])
        #end if

        # update the new pin here
        wallet.set_pin(pin)
        db.session.commit()

        return no_content()
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
            return request_not_found()
        #end if

        # first check if there are any pending otp record
        pending_otp = ForgotPin.query.filter(ForgotPin.wallet_id == wallet.id,\
                               ForgotPin.status == False,\
                               ForgotPin.valid_until > datetime.now() \
                            ).count()
        if pending_otp > 0:
            return bad_request(ERROR["PENDING_OTP"])
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
            return request_not_found()
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
