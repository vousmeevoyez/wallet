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
from app.api.utility.utils import validate_uuid
from app.api.utility.utils import Sms
from app.api.utility.utils import QR
# models
from app.api.models import *
# serializer
from app.api.serializer import UserSchema
from app.api.serializer import WalletSchema
from app.api.serializer import TransactionSchema
from app.api.serializer import VirtualAccountSchema
# http error
from app.api.http_response import created
from app.api.http_response import no_content
# exception
from app.api.error.http import *
from app.api.utility.modules.sms_services import SmsError
# configuration
from app.config import config

STATUS_CONFIG = config.Config.STATUS_CONFIG
TRANSACTION_NOTES = config.Config.TRANSACTION_NOTES
WALLET_CONFIG = config.Config.WALLET_CONFIG
ERROR_CONFIG = config.Config.ERROR_CONFIG

class WalletServices:
    """ Wallet Services Class"""

    def __init__(self, wallet_id):
        wallet_record = Wallet.query.filter_by(id=validate_uuid(wallet_id),
                                               status=STATUS_CONFIG["ACTIVE"]).first()
        if wallet_record is None:
            raise RequestNotFound(ERROR_CONFIG["WALLET_NOT_FOUND"]["TITLE"],
                                  ERROR_CONFIG["WALLET_NOT_FOUND"]["MESSAGE"])
        #end if
        self.wallet = wallet_record

    @staticmethod
    def add(user, wallet, pin):
        """
            create wallet record
            args:
                params -- name, msisdn, user_id, pin
                session -- database session (optional)
        """
        wallet.user_id = user.id
        wallet.set_pin(pin)
        try:
            db.session.add(wallet)
            db.session.commit()
        except IntegrityError as error:
            #print(error.origin)
            db.session.rollback()
            raise UnprocessableEntity(ERROR_CONFIG["DUPLICATE_WALLET"]["TITLE"],
                                      ERROR_CONFIG["DUPLICATE_WALLET"]["MESSAGE"])
        #end try
        response = {
            "wallet_id" : str(wallet.id)
        }
        return created(response)
    #end def

    @staticmethod
    def show(user):
        """
            function to show all user wallet
            args -- params
        """
        response = WalletSchema(many=True).dump(user.wallets).data
        return response
    #end def

    def info(self):
        """
            function to return wallet information
            args:
                params --
        """
        wallet_information = WalletSchema().dump(self.wallet).data

        response = {
            "wallet" : wallet_information
        }
        return response
    #end def

    def remove(self):
        """ remove wallet but just change it to deactivate """
        #cannot delete wallet if this the only wallet
        user_id = self.wallet.user_id
        wallet_number = Wallet.query.filter_by(user_id=user_id).count()
        if wallet_number <= 1:
            raise UnprocessableEntity(ERROR_CONFIG["ONLY_WALLET"]["TITLE"],
                                      ERROR_CONFIG["ONLY_WALLET"]["MESSAGE"])
        #end if

        self.wallet.status = 0 # deactive
        db.session.commit()
        return no_content()
    #end def

    def check_balance(self):
        """
            function to check wallet balance
            args:
                params -- id, pin
        """
        response = {
            "id"      : str(self.wallet.id),
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
                                     exclude=["payment_details","wallet_id"]).\
                                     dump(wallet_response).data
        return response
    #end def

    def history_details(self, transaction_id):
        """
            function to check wallet transaction details
            args :
                wallet_id --
                transaction_id --
        """
        history_details = Transaction.query.filter_by(wallet_id=self.wallet.id,\
                                                      id=validate_uuid(transaction_id)).first()
        if history_details is None:
            raise RequestNotFound(ERROR_CONFIG["TRANSACTION_NOT_FOUND"]["TITLE"],
                                  ERROR_CONFIG["TRANSACTION_NOT_FOUND"]["MESSAGE"])
        #end if
        response = TransactionSchema().dump(history_details).data
        return response
    #end def

    def update_pin(self, params):
        """
            function to update wallet pin
            args :
                params --
        """
        old_pin     = params["old_pin"]
        pin         = params["pin"]
        confirm_pin = params["confirm_pin"]

        # first make sure the old pin is correct
        if self.wallet.check_pin(old_pin) is not True:
            raise UnprocessableEntity(ERROR_CONFIG["INCORRECT_PIN"]["TITLE"],
                                      ERROR_CONFIG["INCORRECT_PIN"]["MESSAGE"])
        #end if

        # second need to check pin and confirmation pin must same
        if pin != confirm_pin:
            raise UnprocessableEntity(ERROR_CONFIG["UNMATCH_PIN"]["TITLE"],
                                      ERROR_CONFIG["UNMATCH_PIN"]["MESSAGE"])
        #end if

        # third make sure the new pin is not the same with the old one
        if self.wallet.check_pin(pin) is True:
            raise UnprocessableEntity(ERROR_CONFIG["DUPLICATE_PIN"]["TITLE"],
                                      ERROR_CONFIG["DUPLICATE_PIN"]["MESSAGE"])
        #end if

        # update the new pin here
        self.wallet.set_pin(pin)
        db.session.commit()

        return no_content()
    #end def

    def send_forgot_otp(self):
        """
            function to send forgot otp to user phone
            args :
                wallet_id
        """
        # first check if there are any pending otp record
        pending_otp = ForgotPin.query.filter(ForgotPin.wallet_id == self.wallet.id,\
                                             ForgotPin.status == False,\
                                             ForgotPin.valid_until > datetime.now() \
                                            ).count()
        if pending_otp > 0:
            raise UnprocessableEntity(ERROR_CONFIG["PENDING_OTP"]["TITLE"],
                                      ERROR_CONFIG["PENDING_OTP"]["MESSAGE"])
        #end if

        # second generate random verify otp number to user phone
        start_range = 1000
        end_range = 9999
        otp_code = random.randint(start_range, end_range)

        # third add record to database contain hashed otp code
        valid_until = datetime.now() + timedelta(minutes=WALLET_CONFIG["OTP_TIMEOUT"])
        forgot_pin = ForgotPin(
            wallet_id=self.wallet.id,
            valid_until=valid_until,
        )
        forgot_pin.set_otp_code(str(otp_code))
        otp_key = forgot_pin.generate_otp_key()
        db.session.add(forgot_pin)

        # fourth send the forgot otp sms to user phone
        # fetch required information for sending sms here
        msisdn = str(self.wallet.user.phone_ext) + str(self.wallet.user.phone_number)
        try:
            Sms().send(msisdn, "FORGOT_PIN", otp_code)
        except SmsError:
            db.session.rollback()
            raise UnprocessableEntity(ERROR_CONFIG["SMS_FAILED"]["TITLE"],
                                      ERROR_CONFIG["SMS_FAILED"]["MESSAGE"])
        #end try
        db.session.commit()
        response = {
            "otp_key" : otp_key,
            "otp_code" : str(otp_code)
        }
        return created(response)
    #end def

    def verify_forgot_otp(self, params):
        """
            function to verify forgot otp to user phone
            args :
                params -- parameter
        """
        otp_code  = params["otp_code"]
        otp_key   = params["otp_key"]
        pin       = params["pin"]

        # fetch forgot otp record
        forgot_otp = ForgotPin.query.filter_by(
            wallet_id=self.wallet.id,
            otp_key=otp_key
        ).first()

        if forgot_otp is None:
            raise RequestNotFound(ERROR_CONFIG["FORGOT_OTP_NOT_FOUND"]["TITLE"],
                                  ERROR_CONFIG["FORGOT_OTP_NOT_FOUND"]["MESSAGE"])
        #end if

        if forgot_otp.status is not False:
            raise UnprocessableEntity(ERROR_CONFIG["OTP_ALREADY_VERIFIED"]["TITLE"],
                                      ERROR_CONFIG["OTP_ALREADY_VERIFIED"]["MESSAGE"])
        #end if

        if forgot_otp.check_otp_code(otp_code) is not True:
            raise UnprocessableEntity(ERROR_CONFIG["INVALID_OTP_CODE"]["TITLE"],
                                      ERROR_CONFIG["INVALID_OTP_CODE"]["MESSAGE"])
        #end if

        # update otp record to DONE
        forgot_otp.status = True

        # set new pin here
        self.wallet.set_pin(pin)
        db.session.commit()

        return no_content()
    #end def

    def get_qr(self):
        """
            function to return encrypted wallet qr
            args:
                params --
        """
        # build qr payload here
        qr_data = {"wallet_id" : str(self.wallet.id)}
        qr_string = QR().generate(qr_data)

        response = {
            "qr_string" : qr_string
        }
        return response
    #end def

    def owner_info(self):
        """
            function to return wallet owner information
        """
        user_info = UserSchema(only=('name',
                                     'msisdn')).dump(self.wallet.user).data
        response = {"user_info" : user_info}
        return response
    #end def

    def check(self, pin):
        """
            function to check and verify pin
        """
        # first make sure the old pin is correct
        if self.wallet.check_pin(pin) is not True:
            raise UnprocessableEntity(ERROR_CONFIG["INCORRECT_PIN"]["TITLE"],
                                      ERROR_CONFIG["INCORRECT_PIN"]["MESSAGE"])
        #end if
        response = {
            "message" : "PIN VERIFIED"
        }
        return response
    #end def
#end class
