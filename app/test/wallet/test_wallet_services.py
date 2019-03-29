"""
    Test Wallet Services
"""
from unittest.mock import patch, Mock
from app.api import db

from app.test.base import BaseTestCase

from app.api.models import *

from app.api.utility.utils import Sms

from app.api.utility.modules.sms_services import SmsError

from app.api.error.http import *

from app.api.wallet.modules.wallet_services import WalletServices

class TestWalletServices(BaseTestCase):
    """ Test Class for Wallet Services"""

    def setUp(self):
        super().setUp()
        """
            CREATE DUMMY WALLET HERE
        """
        wallet = Wallet()
        result = WalletServices.add(self.user, wallet, "123456")

        self.wallet_id = result[0]["data"]["wallet_id"]
    #end def

    def test_wallet_owner_info(self):
        result = WalletServices(self.wallet_id).owner_info()[0]
        self.assertTrue(result["data"])

    def test_add_wallet(self):
        """ test method for creating wallet"""
        self.assertTrue(self.wallet_id)

    def test_show_wallet(self):
        """ test show wallet """
        result = WalletServices.show(self.user)
        self.assertTrue(len(result) > 0)

    def test_wallet_info(self):
        """ test method for get wallet info """
        result = WalletServices(self.wallet_id).info()[0]
        self.assertTrue(result["data"])

    def test_wallet_info_failed_invalid_id(self):
        """ test method for get wallet info but not found """
        with self.assertRaises(BadRequest):
            result = WalletServices("1234").info()

    def test_wallet_remove_failed_only_wallet(self):
        """ test method for removing wallet but failed because wallet can't be
        less than zero """
        with self.assertRaises(UnprocessableEntity):
            result = WalletServices(self.wallet_id).remove()

    def test_wallet_check_pin(self):
        """ test checking wallet balance"""
        result = WalletServices(self.wallet_id).check("123456")
        self.assertEqual(result[0]['data']["message"], "PIN VERIFIED")

        with self.assertRaises(UnprocessableEntity):
            result = WalletServices(self.wallet_id).check("113456")

        with self.assertRaises(UnprocessableEntity):
            result = WalletServices(self.wallet_id).check("113456")

        with self.assertRaises(UnprocessableEntity):
            result = WalletServices(self.wallet_id).check("113456")

        result = WalletServices(self.wallet_id).check("123456")

        with self.assertRaises(UnprocessableEntity):
            result = WalletServices(self.wallet_id).check("113456")

    def test_wallet_balance(self):
        """ test checking wallet balance"""
        result = WalletServices(self.wallet_id).check_balance()[0]["data"]
        self.assertEqual(result["balance"], 0)

    def test_wallet_not_found(self):
        """ test method for checking wallet balance but not found"""
        with self.assertRaises(BadRequest):
            result = WalletServices("123456").check_balance()

    def test_wallet_in_history(self):
        """ test method for checking wallet in transaction on wallet history """
        params = {
            "start_date" : "2019/02/01",
            "end_date" : "2019/02/02",
            "flag" : "IN"
        }
        result = WalletServices(self.wallet_id).history(params)[0]["data"]
        self.assertEqual(result, [])

    def test_wallet_out_history(self):
        """ test method for checking wallet out transaction on wallet history """
        result = WalletServices(self.wallet_id).history({
                                           "start_date" : "2019/02/01",
                                           "end_date" : "2019/02/02",
                                           "flag" : "OUT"})[0]["data"]
        self.assertEqual(result, [])

    @patch.object(Sms, "send")
    def test_send_forgot_otp_success(self, mock_send_sms):
        """ test method for sending forgot otp sms """
        mock_send_sms.return_value = "test"

        result = WalletServices(self.wallet_id).send_forgot_otp()
        self.assertTrue(result[0]["data"]["otp_key"])

    def test_send_forgot_otp_failed_wallet_not_found(self):
        """ test method for sending forgot otp sms but wallet id is not found"""
        with self.assertRaises(BadRequest):
            result = WalletServices("1234").send_forgot_otp()

    @patch.object(Sms, "send")
    def test_send_forgot_otp_failed_pending(self, mock_send_sms):
        """ test method for sending forgot otp sms but there's still pending
        request"""
        mock_send_sms.return_value = "test"
        result = WalletServices(self.wallet_id).send_forgot_otp()
        self.assertTrue(result[0]["data"]["otp_key"])

        with self.assertRaises(UnprocessableEntity):
            result = WalletServices(self.wallet_id).send_forgot_otp()

    @patch.object(Sms, "send")
    def test_send_forgot_otp_failed_raise_sms_error(self, mock_send_sms):
        """ test method for sending forgot otp sms but there's an error when
        sending the message """
        mock_send_sms.side_effect = SmsError(Mock())
        with self.assertRaises(UnprocessableEntity):
            result = WalletServices(self.wallet_id).send_forgot_otp()

    def test_get_qr(self):
        """ test method to generate qr code wallet """
        result = WalletServices(self.wallet_id).get_qr()[0]["data"]
        self.assertTrue(result["qr_string"])

    @patch.object(Sms, "send")
    def test_verify_forgot_otp(self, mock_send_sms):
        """ test method for sending forgot otp sms """
        mock_send_sms.return_value = "test"

        result = WalletServices(self.wallet_id).send_forgot_otp()
        otp_code = result[0]["data"]["otp_code"]
        otp_key = result[0]["data"]["otp_key"]

        result = WalletServices(self.wallet_id).verify_forgot_otp({
            "otp_code" : otp_code,
            "otp_key"  : otp_key,
            "pin"      : "111111",
        })
        self.assertEqual(result[1], 204)

    @patch.object(Sms, "send")
    def test_verify_forgot_otp_but_already_verified(self, mock_send_sms):
        """ test method for sending forgot otp sms but already veirfied"""
        mock_send_sms.return_value = "test"

        result = WalletServices(self.wallet_id).send_forgot_otp()
        otp_code = result[0]["data"]["otp_code"]
        otp_key = result[0]["data"]["otp_key"]

        result = WalletServices(self.wallet_id).verify_forgot_otp({
            "otp_code" : otp_code,
            "otp_key"  : otp_key,
            "pin"      : "111111",
        })
        self.assertEqual(result[1], 204)

        with self.assertRaises(UnprocessableEntity):
            result = WalletServices(self.wallet_id).verify_forgot_otp({
                "otp_code" : otp_code,
                "otp_key"  : otp_key,
                "pin"      : "111111",
            })

    @patch.object(Sms, "send")
    def test_verify_forgot_otp_but_invalid_otp_code(self, mock_send_sms):
        """ test method for sending forgot otp sms but already veirfied"""
        mock_send_sms.return_value = "test"

        result = WalletServices(self.wallet_id).send_forgot_otp()
        otp_code = result[0]["data"]["otp_code"]
        otp_key = result[0]["data"]["otp_key"]

        with self.assertRaises(UnprocessableEntity):
            result = WalletServices(self.wallet_id).verify_forgot_otp({
                "otp_code" : "1234",
                "otp_key"  : otp_key,
                "pin"      : "111111",
            })

    @patch.object(Sms, "send")
    def test_verify_forgot_otp_but_invalid_otp_code(self, mock_send_sms):
        """ test method for sending forgot otp sms but already veirfied"""
        mock_send_sms.return_value = "test"

        result = WalletServices(self.wallet_id).send_forgot_otp()
        otp_code = result[0]["data"]["otp_code"]
        otp_key = result[0]["data"]["otp_key"]

        with self.assertRaises(RequestNotFound):
            result = WalletServices(self.wallet_id).verify_forgot_otp({
                "otp_code" : "1234",
                "otp_key"  : "46464654654654",
                "pin"      : "111111",
            })
