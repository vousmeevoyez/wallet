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
from app.api.common.helper import Sms
from app.api.common.helper import QR

# models
from app.api.models import *

# serializer
from app.api.serializer import WalletSchema
from app.api.serializer import TransactionSchema
from app.api.serializer import VirtualAccountSchema

# http error
from app.api.http_response import created
from app.api.http_response import no_content

# exception
from app.api.exception.common import SmsError

from app.api.exception.wallet import *

from app.api.exception.user import UserNotFoundError

# configuration
from app.config import config

STATUS_CONFIG = config.Config.STATUS_CONFIG
TRANSACTION_NOTES = config.Config.TRANSACTION_NOTES
WALLET_CONFIG = config.Config.WALLET_CONFIG

class WalletServices:
    """ Wallet Services Class"""

    def __init__(self, wallet_id=None, user_id=None):
        wallet_record = None
        if wallet_id is not None:
            wallet_record = Wallet.query.filter_by(id=wallet_id,
                                                   status=STATUS_CONFIG["ACTIVE"]).first()
            if wallet_record is None:
                raise WalletNotFoundError(str(wallet_id))
            #end if

        user_record = None
        if user_id is not None:
            user_record = User.query.filter_by(id=user_id, status=STATUS_CONFIG["ACTIVE"]).first()
            if user_record is None:
                raise UserNotFoundError
        #end if
        self.wallet = wallet_record
        self.user = user_record

    @staticmethod
    def add(wallet, user_id, pin):
        """
            create wallet record
            args:
                params -- name, msisdn, user_id, pin
                session -- database session (optional)
        """
        wallet.user_id = user_id
        wallet.set_pin(pin)
        wallet.generate_wallet_id()
        try:
            db.session.add(wallet)
            db.session.commit()
        except IntegrityError as error:
            #print(error.origin)
            db.session.rollback()
            raise DuplicateWalletError
        #end try
        response = {
            "wallet_id" : str(wallet.id)
        }
        return created(response)
    #end def

    def show(self):
        """
            function to show all user wallet
            args -- params
        """
        response = WalletSchema(many=True).dump(self.user.wallets).data
        return response
    #end def

    def info(self):
        """
            function to return wallet information
            args:
                params --
        """
        wallet_information = WalletSchema().dump(self.wallet).data
        va_information = VirtualAccountSchema(many=True).dump(self.wallet.virtual_accounts).data

        response = {
            "wallet" : wallet_information,
            "virtual_account" : va_information
        }
        return response
    #end def

    def remove(self):
        """ remove wallet but just change it to deactivate """
        #cannot delete wallet if this the only wallet
        user_id = self.wallet.user_id
        wallet_number = Wallet.query.filter_by(user_id=user_id).count()
        if wallet_number <= 1:
            raise OnlyWalletError
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

    def history_details(self, transaction_id):
        """
            function to check wallet transaction details
            args :
                wallet_id --
                transaction_id --
        """
        history_details = Transaction.query.filter_by(wallet_id=self.wallet.id,\
                                                      id=transaction_id).first()
        if history_details is None:
            raise TransactionDetailsNotFoundError
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
            raise IncorrectPinError
        #end if

        # second need to check pin and confirmation pin must same
        if pin != confirm_pin:
            raise UnmatchPinError
        #end if

        # third make sure the new pin is not the same with the old one
        if self.wallet.check_pin(pin) is True:
            raise DuplicatePinError
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
            raise PendingOtpError
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
            raise WalletOtpError
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
            raise OtpNotFoundError
        #end if

        if forgot_otp.status is not False:
            raise OtpVerifiedError
        #end if

        if forgot_otp.check_otp_code(otp_code) is not True:
            raise InvalidOtpError
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
        response = {}
        # build qr payload here
        qr_data = {"wallet_id" : self.wallet.id}
        qr_string = QR().generate(qr_data)

        response["data"] = {
            "qr_string" : qr_string
        }
        return response
    #end def
#end class
