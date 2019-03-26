"""
    Bank Routes
"""
from unittest.mock import Mock, patch

from app.test.base import BaseTestCase

class TestBankRoutes(BaseTestCase):
    """ Test Class for Bank Routes"""
    def setUp(self):
        super().setUp()

        result = self.get_access_token("MODANAADMIN", "password")
        response = result.get_json()

        access_token = response["data"]["access_token"]

        self._token = access_token
    #end def

    def test_check_bni_balance_offline(self):
        result = self.check_bni_balance("123456", self._token)
        response = result.get_json()
        self.assertEqual(result.status_code, 422)
        self.assertEqual(response["error"], "BANK_PROCESS_FAILED")
        self.assertEqual(response["message"], "TIMEOUT")

    def test_check_bni_inquiry_offline(self):
        result = self.check_bni_inquiry("123456", self._token)
        response = result.get_json()
        self.assertEqual(result.status_code, 422)
        self.assertEqual(response["error"], "BANK_PROCESS_FAILED")
        self.assertEqual(response["message"], "TIMEOUT")

    def test_check_bni_payment_offline(self):
        result = self.check_bni_payment("123456", self._token)
        response = result.get_json()
        self.assertEqual(result.status_code, 422)
        self.assertEqual(response["error"], "BANK_PROCESS_FAILED")
        self.assertEqual(response["message"], "TIMEOUT")

    def test_void_bni_payment_offline(self):
        data = {
            "reference_number" : "123456",
            "account_no"       : "123456",
            "amount"           : "1000"
        }
        result = self.void_bni_payment(data, self._token)
        response = result.get_json()
        self.assertEqual(result.status_code, 422)
        self.assertEqual(response["error"], "BANK_PROCESS_FAILED")
        self.assertEqual(response["message"], "TIMEOUT")

    def test_bni_do_payment_offline(self):
        data = {
            "method"         : "0",
            "source_account" : "113183203",
            "account_no"     : "115471119",
            "amount"         : "100500",
            "email"          : "jennie@blackpink.com",
            "clearing_code"  : "CENAIDJAXXX",
            "account_name"   : "Jennie",
            "address"        : "Jl. Buntu",
            "charge_mode"    : "OUR",
        }
        result = self.bni_do_payment(data, self._token)
        response = result.get_json()
        self.assertEqual(result.status_code, 422)
        self.assertEqual(response["error"], "BANK_PROCESS_FAILED")
        self.assertEqual(response["message"], "TIMEOUT")

    def test_bni_interbank_inquiry_offline(self):
        data = {
            "source_account" : "113183203",
            "account_no"     : "115471119",
            "bank_code"      : "014",
        }
        result = self.bni_interbank_inquiry(data, self._token)
        response = result.get_json()
        self.assertEqual(result.status_code, 422)
        self.assertEqual(response["error"], "BANK_PROCESS_FAILED")
        self.assertEqual(response["message"], "TIMEOUT")

    def test_bni_interbank_payment_offline(self):
        data = {
            "amount"         : "10000",
            "source_account" : "115471119",
            "account_no"     : "3333333333",
            "account_name"   : "Jennie",
            "bank_code"      : "014",
            "bank_name"      : "BCA",
            "transfer_ref"   : "100000000024",
        }
        result = self.bni_interbank_payment(data, self._token)
        response = result.get_json()
        self.assertEqual(result.status_code, 422)
        self.assertEqual(response["error"], "BANK_PROCESS_FAILED")
        self.assertEqual(response["message"], "TIMEOUT")
