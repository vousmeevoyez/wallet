"""
    Wallet Services
    ________________
    This is module that serve everything related to wallet
"""
# pylint: disable=bad-whitespace
# pylint: disable=no-self-use
import random
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError

from app.api import db

# helper
from app.api.utility.utils import Sms, QR

# models
from app.api.models import *

# serializer
from app.api.serializer import (
    UserSchema,
    WalletSchema,
    TransactionSchema,
    VirtualAccountSchema,
)

# core
from app.api.wallets.modules.wallet_core import WalletCore
from app.api.virtual_accounts.modules.va_services import VirtualAccountServices
from app.api.quotas.modules.quota_services import QuotaServices

# error
from app.api.const import ERROR as error_response

# http error
from app.lib.http_response import *

# exception
from app.lib.http_error import *
from app.api.utility.utils import UtilityError


class WalletServices(WalletCore):
    """ Wallet Services Class"""

    def add(self, user, wallet, pin):
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
            # print(error.origin)
            db.session.rollback()
            raise UnprocessableEntity(
                error_response["DUPLICATE_WALLET"]["TITLE"],
                error_response["DUPLICATE_WALLET"]["MESSAGE"],
            )
        # end try

        # automatically create virtual account for additional wallet here
        # need to check whether company or personal
        va_name = wallet.user.name
        if wallet.label == "COMPANY":
            va_name = wallet.user.organization

        try:
            virtual_account = VirtualAccount(name=va_name)
            va_payload = {
                "bank_code": "009",
                "type": "CREDIT",
                "wallet_id": str(wallet.id),
                "amount": 0,
            }
            result = VirtualAccountServices().add(virtual_account, va_payload)
        except UnprocessableEntity as error:
            # raise CommitError(error.msg, None, error.title, None)
            pass

        # we automatically create quota for newly generated wallet
        quota_info = QuotaServices(wallet_id=wallet.id).add(is_custom=False)

        response = {"wallet_id": str(wallet.id)}
        return created(response)

    # end def

    @staticmethod
    def show(user):
        """
            function to show all user wallet
            args -- params
        """
        wallets = WalletSchema(many=True).dump(user.wallets).data
        return ok(wallets)

    # end def

    def info(self):
        """
            function to return wallet information
            args:
                params --
        """
        wallet = WalletSchema().dump(self.source).data
        return ok(wallet)

    # end def

    def remove(self):
        """ remove wallet but just change it to deactivate """
        # cannot delete wallet if this the only wallet
        user_id = self.source.user_id
        wallet_number = Wallet.query.filter_by(user_id=user_id).count()
        if wallet_number <= 1:
            raise UnprocessableEntity(
                error_response["ONLY_WALLET"]["TITLE"],
                error_response["ONLY_WALLET"]["MESSAGE"],
            )
        # end if

        self.source.status = 0  # deactive
        db.session.commit()
        return no_content()

    # end def

    def check_balance(self):
        """
            function to check wallet balance
            args:
                params -- id, pin
        """
        response = {"id": str(self.source.id), "balance": self.source.balance}
        return ok(response)

    # end def

    def update_pin(self, params):
        """
            function to update wallet pin
            args :
                params --
        """
        pin = params["pin"]
        confirm_pin = params["confirm_pin"]

        # first need to check pin and confirmation pin must same
        if pin != confirm_pin:
            raise UnprocessableEntity(
                error_response["UNMATCH_PIN"]["TITLE"],
                error_response["UNMATCH_PIN"]["MESSAGE"],
            )
        # end if

        # second make sure the new pin is not the same with the old one
        if self.source.check_pin(pin) == "CORRECT":
            raise UnprocessableEntity(
                error_response["DUPLICATE_PIN"]["TITLE"],
                error_response["DUPLICATE_PIN"]["MESSAGE"],
            )
        # end if

        # update the new pin here
        self.source.set_pin(pin)
        db.session.commit()

        return no_content()

    # end def

    def send_forgot_otp(self):
        """
            function to send forgot otp to user phone
            args :
                wallet_id
        """
        # first check if there are any pending otp record
        pending_otp = ForgotPin.query.filter(
            ForgotPin.wallet_id == self.source.id,
            ForgotPin.status == False,
            ForgotPin.valid_until > datetime.now(),
        ).count()
        if pending_otp > 0:
            raise UnprocessableEntity(
                error_response["PENDING_OTP"]["TITLE"],
                error_response["PENDING_OTP"]["MESSAGE"],
            )
        # end if

        # second generate random verify otp number to user phone
        start_range = 100000
        end_range = 999999
        otp_code = random.randint(start_range, end_range)

        # third add record to database contain hashed otp code
        valid_until = datetime.now() + timedelta(minutes=WALLET["OTP_TIMEOUT"])
        forgot_pin = ForgotPin(wallet_id=self.source.id, valid_until=valid_until)
        forgot_pin.set_otp_code(str(otp_code))
        otp_key = forgot_pin.generate_otp_key()
        db.session.add(forgot_pin)

        # fourth send the forgot otp sms to user phone
        # fetch required information for sending sms here
        msisdn = str(self.source.user.phone_ext) + str(self.source.user.phone_number)
        try:
            Sms().send(msisdn, "FORGOT_PIN", otp_code)
        except UtilityError:
            db.session.rollback()
            raise UnprocessableEntity(
                error_response["SMS_FAILED"]["TITLE"],
                error_response["SMS_FAILED"]["MESSAGE"],
            )
        # end try
        db.session.commit()
        response = {"otp_key": otp_key, "otp_code": str(otp_code)}
        return created(response)

    # end def

    def verify_forgot_otp(self, params):
        """
            function to verify forgot otp to user phone
            args :
                params -- parameter
        """
        otp_code = params["otp_code"]
        otp_key = params["otp_key"]
        pin = params["pin"]

        # fetch forgot otp record
        forgot_otp = ForgotPin.query.filter_by(
            wallet_id=self.source.id, otp_key=otp_key
        ).first()

        if forgot_otp is None:
            raise RequestNotFound(
                error_response["FORGOT_OTP_NOT_FOUND"]["TITLE"],
                error_response["FORGOT_OTP_NOT_FOUND"]["MESSAGE"],
            )
        # end if

        if forgot_otp.status is not False:
            raise UnprocessableEntity(
                error_response["OTP_ALREADY_VERIFIED"]["TITLE"],
                error_response["OTP_ALREADY_VERIFIED"]["MESSAGE"],
            )
        # end if

        if forgot_otp.check_otp_code(otp_code) is not True:
            raise UnprocessableEntity(
                error_response["INVALID_OTP_CODE"]["TITLE"],
                error_response["INVALID_OTP_CODE"]["MESSAGE"],
            )
        # end if

        # update otp record to DONE
        forgot_otp.status = True

        # set new pin here
        self.source.set_pin(pin)
        db.session.commit()

        return no_content()

    # end def

    def get_qr(self):
        """
            function to return encrypted wallet qr
            args:
                params --
        """
        # build qr payload here
        qr_data = {"wallet_id": str(self.source.id)}
        qr_string = QR().generate(qr_data)

        return ok({"qr_string": qr_string})

    # end def

    def owner_info(self):
        """
            function to return wallet owner information
        """
        user_info = (
            UserSchema(only=("name", "msisdn", "wallets.id", "wallets.label"))
            .dump(self.source.user)
            .data
        )
        return ok(user_info)

    # end def

    def check(self):
        """
            function to check and verify pin
        """
        response = {"message": "PIN VERIFIED"}
        return ok(response)

    # end def


# end class
