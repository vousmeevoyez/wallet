""" 
    Test Bank Services
    ___________________
    test bank services module
"""
from unittest.mock import Mock, patch

from app.test.base import BaseTestCase
from app.api.bank.modules.bank_services import BankServices

class TestMockBankServices(BaseTestCase):
    """ Test Class by mocking Bank Services"""

    def test_get_banks(self):
        """ test function that return all available banks"""
        result = BankServices().get_banks()
        self.assertIsInstance(result["data"], list)
        self.assertTrue(len(result["data"]) > 0)

    @patch.object(BankServices, "get_host_balance")
    def test_get_host_balance(self, mock_bank_services):
        """ test function that host balance information"""
        expected_value = {
            "bank_account_info" : {
                "customer_name" : "some customer name",
                "balance" : "909909090909"
            }
        }
        mock_bank_services.return_value = expected_value
        result = BankServices().get_host_balance("123456")
        self.assertEqual(result, expected_value)

    @patch.object(BankServices, "get_account_information")
    def test_get_account_information(self, mock_bank_services):
        """ test function that check BNI Information """
        expected_value = {
            "bank_account_info" : {
                "account_no"    : "123412313123121312",
                "customer_name" : "some customer name",
                "status"        : "1",
                "account_type"  : "007",
                "type"          : "BANK_ACCOUNT", # BANK // VA
            }
        }
        mock_bank_services.return_value = expected_value
        result = BankServices().get_account_information("123456")
        self.assertEqual(result, expected_value)
