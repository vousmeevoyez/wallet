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

    def _create_wallet(self):
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

        result = WalletServices.add({"user_id" : user.id, "pin" : "123456"})
        response = {
            "user_id" : user.id,
            "wallet_id" : result[0]["wallet_id"],
        }
        return response
    #end def

    def test_add_wallet(self):
        """ test method for creating wallet"""
        response = self._create_wallet()
        self.assertTrue(response["user_id"])
        self.assertTrue(response["wallet_id"])

    def test_show_wallet(self):
        """ test show wallet """
        result = WalletServices.show()
        self.assertEqual(result, [])

    def test_wallet_info(self):
        """ test method for get wallet info """
        response = self._create_wallet()

        wallet_id = response["wallet_id"]

        result = WalletServices().info({"wallet_id" : wallet_id})
        self.assertTrue(result["wallet"])

    '''
    def test_wallet_info_failed_not_found(self):
        """ test method for get wallet info but not found """
        result = WalletServices("1234").info()
        self.assertTrue(result[1], 404)

    def test_wallet_remove_failed_only_wallet(self):
        """ test method for removing wallet but failed because wallet can't be
        less than zero """

        response = self._create_wallet()

        wallet_id = response["wallet_id"]

        result = WalletServices(wallet_id).remove()
        self.assertEqual(result[1], 400)


    def test_wallet_remove(self):
        """ test method for removing wallet """

        response = self._create_wallet()

        user_id = response["user_id"]
        wallet_id = response["wallet_id"]

        result = WalletServices().add({"user_id" : user_id, "pin" : "123456"})
        self.assertEqual(result[1], 201) # created

        result = WalletServices().remove({"id" : result[0]["wallet_id"]})
        self.assertEqual(result[1], 204) # no content

    def test_wallet_balance(self):
        """ test method for checking wallet balance """

        response = self._create_wallet()

        wallet_id = response["wallet_id"]

        result = WalletServices().check_balance({"id" : wallet_id,
                                                 "pin" : "123456"})
        self.assertEqual(result["balance"], 0)

    def test_wallet_not_found(self):
        """ test method for checking wallet balance but not found"""
        result = WalletServices().check_balance({"id" : "12345",
                                                 "pin" : "123456"})
        self.assertEqual(result[1], 404)

    def test_wallet_incorrect_pin(self):
        """ test method for checking wallet balance but pin is incorrect """

        response = self._create_wallet()

        wallet_id = response["wallet_id"]
        result = WalletServices().check_balance({"id" : wallet_id,
                                                 "pin" : "113456"})
        self.assertEqual(result[1], 400)

    def test_wallet_in_history(self):
        """ test method for checking wallet in transaction on wallet history """

        response = self._create_wallet()

        wallet_id = response["wallet_id"]

        result = WalletServices().history({"wallet_id" : wallet_id,
                                           "start_date" : "2019/02/01",
                                           "end_date" : "2019/02/02",
                                           "flag" : "IN"})
        self.assertEqual(result, [])

    def test_wallet_out_history(self):
        """ test method for checking wallet out transaction on wallet history """

        response = self._create_wallet()

        wallet_id = response["wallet_id"]

        result = WalletServices().history({"wallet_id" : wallet_id,
                                           "start_date" : "2019/02/01",
                                           "end_date" : "2019/02/02",
                                           "flag" : "OUT"})
        self.assertEqual(result, [])
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
    '''
