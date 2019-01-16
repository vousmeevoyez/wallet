"""
    Test Wallet Services
"""
from unittest.mock import patch, Mock
from app.api import db

from app.test.base          import BaseTestCase

from app.api.models         import Payment
from app.api.models         import Wallet
from app.api.models         import User
from app.api.models         import ForgotPin

from app.api.wallet.modules.wallet_services import WalletServices

class TestWalletServices(BaseTestCase):
    """ Test Class for Wallet Services"""

    def _create_dummy_user_wallet(self):
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            phone_ext='62',
            phone_number='81219644314',
        )
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        # create dummy wallet and link it to the user
        wallet = Wallet(
            user_id=user.id,
        )
        db.session.add(wallet)
        db.session.commit()
        return wallet
    #end def

    def test_send_forgot_otp_success(self):
        """ test method for sending forgot otp sms """
        wallet = self._create_dummy_user_wallet()

        result = WalletServices().send_forgot_otp(wallet.id)
        self.assertTrue(result["data"]["otp_key"])

    def test_send_forgot_otp_failed_wallet_not_found(self):
        """ test method for sending forgot otp sms but wallet id is not found"""
        result = WalletServices().send_forgot_otp("1234")
        self.assertEqual(result[1], 404)

    def test_send_forgot_otp_failed_pending(self):
        """ test method for sending forgot otp sms but there's still pending
        request"""
        wallet = self._create_dummy_user_wallet()

        result = WalletServices().send_forgot_otp(wallet.id)
        self.assertTrue(result["data"]["otp_key"])

        result = WalletServices().send_forgot_otp(wallet.id)
        self.assertEqual(result[1], 400)

    def test_send_forgot_otp_failed_raise_sms_error(self):
        """ test method for sending forgot otp sms but there's an error when
        sending the message """
        wallet = self._create_dummy_user_wallet()

        result = WalletServices().send_forgot_otp(wallet.id)
        self.assertTrue(result["data"]["otp_key"])

        result = WalletServices().send_forgot_otp(wallet.id)
        self.assertEqual(result[1], 400)

    def test_get_qr(self):
        wallet = self._create_dummy_user_wallet()
        result = WalletServices().get_qr({"id" : wallet.id})
        self.assertTrue(result["data"]["qr_string"])
