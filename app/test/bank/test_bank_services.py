""" 
    Test Bank Services
    ___________________
    test bank services module
"""
from unittest.mock import Mock, patch

from app.test.base import BaseTestCase
from app.api.bank.modules.bank_services import BankServices
from app.api.bank.handler import BankHandler

class TestBankServices(BaseTestCase):
    """ Test Class for Bank Services"""

    def test_get_banks(self):
        """ test function that return all available banks"""
        result = BankServices().get_banks()
        self.assertIsInstance(result["data"], list)
        self.assertTrue(len(result["data"]) > 0)

    @patch.object(BankHandler, "dispatch")
    def test_check_balance_success(self, mock_func):
        """ test function that return successful host account balance"""
        mock_func.return_value = {
            "status" : "SUCCESS",
            "data": {
                "bank_account_info" : {
                    "customer_name" : "MODANA",
                    "balance" : 10000,
                }
            }
        }
        result = BankServices().check_balance("123456")
        self.assertEqual(result["data"]["balance"], 10000)

    @patch.object(BankHandler, "dispatch")
    def test_check_balance_failed(self, mock_func):
        """ test function that failed checking host account balance"""
        mock_func.return_value = {
            "status" : "FAILED",
            "data" : "some error"
        }
        result = BankServices().check_balance("123456")
        self.assertEqual(result[0]["errors"], "some error")
