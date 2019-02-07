"""
    Test Wallet Services
"""
from unittest.mock import patch, Mock
from app.api import db

from app.test.base import BaseTestCase

from app.api.models import *

from app.api.common.helper import Sms

from app.api.exception.common import SmsError

from app.api.exception.wallet import *

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

        wallet = Wallet()
        result = WalletServices.add(wallet, user.id, "123456")
        return result[0]["data"]
    #end def

    def test_add_wallet(self):
        """ test method for creating wallet"""
        response = self._create_wallet()
        self.assertTrue(response["wallet_id"])

    def test_show_wallet(self):
        """ test show wallet """
        result = WalletServices.show()
        self.assertEqual(result, [])

    def test_wallet_info(self):
        """ test method for get wallet info """
        response = self._create_wallet()

        wallet_id = response["wallet_id"]

        result = WalletServices(wallet_id).info()
        self.assertTrue(result["wallet"])

    def test_wallet_info_failed_not_found(self):
        """ test method for get wallet info but not found """
        with self.assertRaises(WalletNotFoundError):
            result = WalletServices("1234").info()

    def test_wallet_remove_failed_only_wallet(self):
        """ test method for removing wallet but failed because wallet can't be
        less than zero """

        response = self._create_wallet()
        wallet_id = response["wallet_id"]

        with self.assertRaises(OnlyWalletError):
            result = WalletServices(wallet_id).remove()

    def test_wallet_balance(self):

        response = self._create_wallet()

        wallet_id = response["wallet_id"]

        result = WalletServices(wallet_id).check_balance()
        self.assertEqual(result["balance"], 0)

    def test_wallet_not_found(self):
        """ test method for checking wallet balance but not found"""
        with self.assertRaises(WalletNotFoundError):
            result = WalletServices("123456").check_balance()

    def test_wallet_in_history(self):
        """ test method for checking wallet in transaction on wallet history """

        response = self._create_wallet()

        wallet_id = response["wallet_id"]

        params = {
            "start_date" : "2019/02/01",
            "end_date" : "2019/02/02",
            "flag" : "IN"
        }
        result = WalletServices(wallet_id).history(params)
        self.assertEqual(result, [])

    def test_wallet_out_history(self):
        """ test method for checking wallet out transaction on wallet history """

        response = self._create_wallet()

        wallet_id = response["wallet_id"]

        result = WalletServices(wallet_id).history({
                                           "start_date" : "2019/02/01",
                                           "end_date" : "2019/02/02",
                                           "flag" : "OUT"})
        self.assertEqual(result, [])

    @patch.object(Sms, "send")
    def test_send_forgot_otp_success(self, mock_send_sms):
        """ test method for sending forgot otp sms """
        response = self._create_wallet()

        wallet_id = response["wallet_id"]

        mock_send_sms.return_value = "test"

        result = WalletServices(wallet_id).send_forgot_otp()
        self.assertTrue(result[0]["data"]["otp_key"])

    def test_send_forgot_otp_failed_wallet_not_found(self):
        """ test method for sending forgot otp sms but wallet id is not found"""
        with self.assertRaises(WalletNotFoundError):
            result = WalletServices("1234").send_forgot_otp()

    @patch.object(Sms, "send")
    def test_send_forgot_otp_failed_pending(self, mock_send_sms):
        """ test method for sending forgot otp sms but there's still pending
        request"""
        response = self._create_wallet()
        wallet_id = response["wallet_id"]

        mock_send_sms.return_value = "test"
        result = WalletServices(wallet_id).send_forgot_otp()
        self.assertTrue(result[0]["data"]["otp_key"])

        with self.assertRaises(PendingOtpError):
            result = WalletServices(wallet_id).send_forgot_otp()

    @patch.object(Sms, "send")
    def test_send_forgot_otp_failed_raise_sms_error(self, mock_send_sms):
        """ test method for sending forgot otp sms but there's an error when
        sending the message """
        response = self._create_wallet()
        wallet_id = response["wallet_id"]

        mock_send_sms.side_effect = SmsError
        with self.assertRaises(WalletOtpError):
            result = WalletServices(wallet_id).send_forgot_otp()

    def test_get_qr(self):
        """ test method to generate qr code wallet """
        response = self._create_wallet()
        wallet_id = response["wallet_id"]

        result = WalletServices(wallet_id).get_qr()
        self.assertTrue(result["data"]["qr_string"])

    @patch.object(Sms, "send")
    def test_verify_forgot_otp(self, mock_send_sms):
        """ test method for sending forgot otp sms """
        response = self._create_wallet()

        wallet_id = response["wallet_id"]

        mock_send_sms.return_value = "test"

        result = WalletServices(wallet_id).send_forgot_otp()
        otp_code = result[0]["data"]["otp_code"]
        otp_key = result[0]["data"]["otp_key"]

        result = WalletServices(wallet_id).verify_forgot_otp({
            "otp_code" : otp_code,
            "otp_key"  : otp_key,
            "pin"      : "111111",
        })
        self.assertEqual(result[1], 204)

    @patch.object(Sms, "send")
    def test_verify_forgot_otp_but_already_verified(self, mock_send_sms):
        """ test method for sending forgot otp sms but already veirfied"""
        response = self._create_wallet()

        wallet_id = response["wallet_id"]

        mock_send_sms.return_value = "test"

        result = WalletServices(wallet_id).send_forgot_otp()
        otp_code = result[0]["data"]["otp_code"]
        otp_key = result[0]["data"]["otp_key"]

        result = WalletServices(wallet_id).verify_forgot_otp({
            "otp_code" : otp_code,
            "otp_key"  : otp_key,
            "pin"      : "111111",
        })
        self.assertEqual(result[1], 204)

        with self.assertRaises(OtpVerifiedError):
            result = WalletServices(wallet_id).verify_forgot_otp({
                "otp_code" : otp_code,
                "otp_key"  : otp_key,
                "pin"      : "111111",
            })

    @patch.object(Sms, "send")
    def test_verify_forgot_otp_but_invalid_otp_code(self, mock_send_sms):
        """ test method for sending forgot otp sms but already veirfied"""
        response = self._create_wallet()

        wallet_id = response["wallet_id"]

        mock_send_sms.return_value = "test"

        result = WalletServices(wallet_id).send_forgot_otp()
        otp_code = result[0]["data"]["otp_code"]
        otp_key = result[0]["data"]["otp_key"]

        with self.assertRaises(InvalidOtpError):
            result = WalletServices(wallet_id).verify_forgot_otp({
                "otp_code" : "1234",
                "otp_key"  : otp_key,
                "pin"      : "111111",
            })

    @patch.object(Sms, "send")
    def test_verify_forgot_otp_but_invalid_otp_code(self, mock_send_sms):
        """ test method for sending forgot otp sms but already veirfied"""
        response = self._create_wallet()

        wallet_id = response["wallet_id"]

        mock_send_sms.return_value = "test"

        result = WalletServices(wallet_id).send_forgot_otp()
        otp_code = result[0]["data"]["otp_code"]
        otp_key = result[0]["data"]["otp_key"]

        with self.assertRaises(OtpNotFoundError):
            result = WalletServices(wallet_id).verify_forgot_otp({
                "otp_code" : "1234",
                "otp_key"  : "46464654654654",
                "pin"      : "111111",
            })
