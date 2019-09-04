"""
    Integration Testing between wallet & routes
"""
import uuid
from unittest.mock import Mock, patch

from app.test.base import BaseTestCase

from app.api.models import User
from app.api.models import Wallet
from app.api import db

class TestWalletRoutes(BaseTestCase):
    """ Test Class for Wallet Routes"""

    def setUp(self):
        super().setUp()

        user1, wallet1 = self.create_dummy_user(self.access_token)

        self._user1 = user1
        self._wallet1 = wallet1

        user2, wallet2 = self.create_dummy_user(self.access_token)

        self._user2 = user2
        self._wallet2 = wallet2
    #end def

    """
        CREATE WALLET
    """
    def test_create_wallet(self):
        """ CREATE_WALLET CASE 1 : Successfully created wallet """
        params = {
            "label" : "wallet label",
            "pin" : "123456"
        }
        result = self.create_wallet(params, self.access_token)
        self.assertEqual(result.status_code, 201)

    def test_create_wallet_serialize_error(self):
        """ CREATE_WALLET CASE 3 : Failed created wallet because some invalid payload """
        params = {
            "label" : "wallet_label", # ALPHABET ONLY
            "pin" : "1" # PIN TOO SHOORT
        }

        result = self.create_wallet(params, self.access_token)
        response = result.get_json()
        self.assertEqual(result.status_code, 400)
        self.assertEqual(response["error"], "INVALID_PARAMETER")
        self.assertTrue(response["details"])

    """
        WALLET INFO
    """
    def test_get_wallet_info(self):
        """ GET_WALLET_INFO CASE 1 : Successfully get wallet information """
        result = self.get_wallet_info(self._wallet1, self.access_token)
        response = result.get_json()
        self.assertTrue(response["data"])

    """
        REMOVE WALLET
    """
    def test_remove_wallet(self):
        """ REMOVE WALLET CASE 1 : Successfully remove wallet """
        params = {
            "label"  : "wallet label",
            "pin"    : "123456"
        }

        result = self.create_wallet(params, self.access_token)
        self.assertEqual(result.status_code, 201)

        params = {
            "label" : "wallet lllabel",
            "pin" : "123456"
        }

        result = self.create_wallet(params, self.access_token)
        self.assertEqual(result.status_code, 201)

        response = result.get_json()
        wallet_id = response["data"]["wallet_id"]

        result = self.remove_wallet(wallet_id, self.access_token)
        self.assertEqual(result.status_code, 204)

        result = self.get_all_wallet(self.access_token)

    def test_remove_wallet_failed(self):
        """ REMOVE WALLET CASE 2 : Failed remove wallet because only wallet """
        result = self.remove_wallet(self._wallet1, self.access_token)
        response = result.get_json()

        self.assertEqual(result.status_code, 422)
        self.assertEqual(response["error"], "ONLY_WALLET")
        self.assertTrue(response["message"])

    """
        GET BALANCE
    """
    def test_get_balance(self):
        """ GET_BALANCE CASE 1 : return wallet balance information """
        result = self.get_balance(self._wallet1, self.access_token)
        response = result.get_json()["data"]
        self.assertTrue(response["id"])

    """
        GET TRANSACTIONS
    """
    def test_get_transactions(self):
        """ GET TRANSACTIONS CASE 1 : Get wallet transaction for specific date"""
        # TEST GETTING IN TRANSACTION
        params = {
            "start_date" : "2019/01/01",
            "end_date"   : "2019/01/03",
            "flag" : "IN"
        }
        result = self.get_transaction(self._wallet1, params, self.access_token)
        response = result.get_json()
        self.assertTrue(result.status_code, 200)
        # TEST GETTING OUT TRANSACTION
        params = {
            "start_date" : "2019/01/01",
            "end_date"   : "2019/01/03",
            "flag" : "OUT"
        }
        result = self.get_transaction(self._wallet1, params, self.access_token)
        response = result.get_json()
        self.assertTrue(result.status_code, 200)
        #TEST GETTING ALL TRANSACTIONS
        params = {
            "start_date" : "2019/01/01",
            "end_date"   : "2019/01/03",
            "flag" : "ALL"
        }
        result = self.get_transaction(self._wallet1, params, self.access_token)
        response = result.get_json()
        self.assertTrue(result.status_code, 200)

    def test_get_transactions_serialize_failed(self):
        """ GET TRANSACTIONS CASE 2 : Get wallet transaction with invalid
        payload """
        # TEST GETTING IN TRANSACTION
        params = {
            "start_date" : "2019-01-01",
            "end_date"   : "2019-01-03",
            "flag" : "KLK"
        }
        result = self.get_transaction(self._wallet1, params, self.access_token)
        response = result.get_json()
        self.assertTrue(result.status_code, 400)

    """
        TRANSACTION DETAILS
    """

    def test_get_transactions_details_success(self):
        """ GET TRANSACTIONS DETAILS 1 : Get wallet transaction details but
        transaction not found"""

        """ TRANSFER MONEY FIRST TO GET TRANSACTION ID"""
        wallet = Wallet.query.get(self._wallet1)
        wallet.balance = 99999999
        db.session.commit()

        params = {
            "amount" : "15",
            "notes" : "some notes",
            "pin" : "123456",
            "types": "PAYROLL"
        }

        result = self.transfer(self._wallet1, self._wallet2, params,
                               self.access_token)
        response = result.get_json()
        self.assertEqual(result.status_code, 202)
        self.assertTrue(response["data"])

        params = {
            "transaction_id" : response['data']['id'],
        }
        result = self.get_transaction_details(self._wallet1, params, self.access_token)
        response = result.get_json()
        self.assertTrue(result.status_code, 200)
        self.assertTrue(response["data"])

    def test_get_transactions_details_failed(self):
        """ GET TRANSACTIONS DETAILS 2 : Get wallet transaction details but
        transaction not found"""
        params = {
            "transaction_id" : str(uuid.uuid4()),
        }
        result = self.get_transaction_details(self._wallet1, params, self.access_token)
        response = result.get_json()
        self.assertTrue(result.status_code, 404)
        self.assertEqual(response["error"], "TRANSACTION_NOT_FOUND")
        self.assertTrue(response["message"])

    """ 
        UPDATE PIN
    """
    def test_update_pin_incorrect_old_pin(self):
        """CASE 1 UPDATE PIN : Incorrect old pin"""
        params = {
            "old_pin"    : "111111",
            "pin"        : "123456",
            "confirm_pin": "123546",
        }
        result = self.update_pin(self._wallet1, params, self.access_token)
        response = result.get_json()
        self.assertEqual(result.status_code, 422)
        self.assertTrue(response["error"])

    def test_update_pin_unmatch_pin(self):
        """ CASE 2 UPDATE PIN : unmatch pin """
        params = {
            "old_pin"    : "123456",
            "pin"        : "123456",
            "confirm_pin": "123546",
        }
        result = self.update_pin(self._wallet1, params, self.access_token)
        self.assertEqual(result.status_code, 422)

    def test_update_pin_old_pin(self):
        """ CASE 3 UPDATE PIN : old pin """
        params = {
            "old_pin"    : "123456",
            "pin"        : "123456",
            "confirm_pin": "123456",
        }
        result = self.update_pin(self._wallet1, params, self.access_token)
        self.assertEqual(result.status_code, 422)

    """
        CHECK PIN
    """
    def test_check_pin(self):
        """CASE 1 CHECK PIN : Check pin successfully"""
        params = {
            "pin" : "123456",
        }
        result = self.check_pin(self._wallet1, params, self.access_token)
        response = result.get_json()
        self.assertEqual(response['data']['message'], "PIN VERIFIED")

    def test_check_pin_incorrect(self):
        """CASE 2 CHECK PIN : Check pin incorrectly """
        params = {
            "pin" : "123452",
        }
        result = self.check_pin(self._wallet1, params, self.access_token)
        response = result.get_json()
        self.assertEqual(response['error'], "INCORRECT_PIN")

        params = {
            "pin" : "123452",
        }
        result = self.check_pin(self._wallet1, params, self.access_token)
        response = result.get_json()
        self.assertEqual(response['error'], "INCORRECT_PIN")

        params = {
            "pin" : "123452",
        }
        result = self.check_pin(self._wallet1, params, self.access_token)
        response = result.get_json()
        self.assertEqual(response['error'], "INCORRECT_PIN")

        params = {
            "pin" : "123452",
        }
        result = self.check_pin(self._wallet1, params, self.access_token)
        response = result.get_json()
        self.assertEqual(response['error'], "MAX_PIN_ATTEMPT")

    """
        QR Code
    """
    def test_get_qr(self):
        """ GET_QR CASE 1 : return qr string"""
        result = self.get_qr(self._wallet1, self.access_token)
        response = result.get_json()["data"]
        self.assertEqual(result.status_code, 200)
        self.assertTrue(response["qr_string"])

    def test_qr_checkout(self):
        """ QR_CHECKOUT CASE 1 : return user info"""
        result = self.get_qr(self._wallet1, self.access_token)
        response = result.get_json()["data"]
        self.assertEqual(result.status_code, 200)
        self.assertTrue(response["qr_string"])

        payload = {
            "qr_string" : response["qr_string"]
        }

        result = self.qr_checkout(self._wallet1, payload, self.access_token)
        response = result.get_json()["data"]
        self.assertTrue(result.status_code, 200)
    """
        FOrgot pin
    """
    def test_forgot_pin(self):
        """ FORGOT PIN CASE 1 : send forgot otp"""
        result = self.forgot_pin(self._wallet1, self.access_token)
        response = result.get_json()

        self.assertEqual(result.status_code, 201)
        self.assertTrue(response["data"])
        self.assertTrue(response["data"]["otp_key"])
        self.assertTrue(response["data"]["otp_code"])

    def test_forgot_pin_pending(self):
        """ FORGOT PIN CASE 2 : send forgot otp there's pending """

        result = self.forgot_pin(self._wallet1, self.access_token)
        response = result.get_json()

        self.assertEqual(result.status_code, 201)
        self.assertTrue(response["data"])
        self.assertTrue(response["data"]["otp_key"])
        self.assertTrue(response["data"]["otp_code"])

        result = self.forgot_pin(self._wallet1, self.access_token)
        response = result.get_json()
        self.assertEqual(result.status_code, 422)
        self.assertEqual(response["error"], "PENDING_OTP")

    """
        Verify Forgot OTP
    """
    def test_verify_forgot_pin(self):
        """ VERIFY FORGOT PIN CASE 1 : verify forgot otp"""
        result = self.forgot_pin(self._wallet1, self.access_token)
        response = result.get_json()

        self.assertEqual(result.status_code, 201)
        self.assertTrue(response["data"])
        self.assertTrue(response["data"]["otp_key"])
        self.assertTrue(response["data"]["otp_code"])

        otp_key = response["data"]["otp_key"]
        otp_code = response["data"]["otp_code"]

        params = {
            "otp_key" : otp_key,
            "otp_code": otp_code,
            "pin" : "12345"
        }

        result = self.verify_forgot_pin(self._wallet1, params, self.access_token)
        self.assertEqual(result.status_code, 204)

    def test_verify_forgot_pin_not_found(self):
        """ VERIFY FORGOT PIN CASE 2 : verify forgot otp not found """
        result = self.forgot_pin(self._wallet1, self.access_token)
        response = result.get_json()

        self.assertEqual(result.status_code, 201)
        self.assertTrue(response["data"])
        self.assertTrue(response["data"]["otp_key"])
        self.assertTrue(response["data"]["otp_code"])

        params = {
            "otp_key" : "12312312312",
            "otp_code": "123456",
            "pin" : "12345"
        }

        result = self.verify_forgot_pin(self._wallet1, params, self.access_token)
        self.assertEqual(result.status_code, 404)

    """
        WITHDRAW 
    """
    def test_withdraw(self):
        """ CASE 1 Withdraw : try success withdraw """
        # inject balance
        wallet = Wallet.query.get(self._wallet1)
        wallet.balance = 99999999
        db.session.commit()

        params = {
            "amount" : "50000",
            "pin" : "123456"
        }

        result = self.withdraw(self._wallet1, params,
                               self.access_token)
        response = result.get_json()["data"]
        self.assertEqual(result.status_code, 200)
        self.assertTrue(response["valid_until"])
        self.assertTrue(response["amount"])

    def test_withdraw_all(self):
        """ CASE 2 Withdraw : try success withdraw all """
        # inject balance
        wallet = Wallet.query.get(self._wallet1)
        wallet.balance = 99999999
        db.session.commit()

        params = {
            "amount" : "0",
            "pin" : "123456"
        }

        result = self.withdraw(self._wallet1, params,
                               self.access_token)
        response = result.get_json()["data"]

        self.assertEqual(result.status_code, 200)
        self.assertTrue(response["valid_until"])
        self.assertTrue(response["amount"])
