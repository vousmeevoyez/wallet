""" 
    Test Bank Services
    ___________________
    test bank services module
"""
from unittest.mock import Mock, patch

from app.test.base import BaseTestCase
from app.api.bank.modules.bank_services import BankServices

from task.bank.BNI.helper import CoreBank
from task.bank.exceptions.general import *
from app.api.error.http import *

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

    @patch.object(CoreBank, "get_balance")
    def test_get_host_balance_timeout(self, mock_bank_services):
        """ test function that host balance information failed """
        mock_bank_services.side_effect = ApiError(
            original_exception="exception original object"
        )
        with self.assertRaises(UnprocessableEntity):
            result = BankServices().get_host_balance("123456")

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

    @patch.object(BankServices, "get_payment_status")
    def test_get_payment_status(self, mock_bank_services):
        """ test function that get BNI payment status"""
        expected_value = {
            "payment_info": {
                "status": "Y",
                "source_account": "0115476117",
                "destination_account": "0115476151",
                "amount": "100000"
            }
        }
        mock_bank_services.return_value = expected_value
        result = BankServices().get_payment_status("123456")
        self.assertEqual(result, expected_value)

    @patch.object(BankServices, "void_payment")
    def test_void_payment(self, mock_bank_services):
        """ test function that void BNI payment"""
        expected_value = {
            "payment_info": {
                "status": "Y",
                "source_account": "0115476117",
                "destination_account": "0115476151",
                "amount": "100000"
            }
        }
        mock_bank_services.return_value = expected_value
        result = BankServices().void_payment("12345", "some_account_no", 10000)
        self.assertEqual(result, expected_value)

    @patch.object(BankServices, "do_payment")
    def test_do_payment(self, mock_bank_services):
        """ test function that void BNI payment"""
        expected_value = {
            'transfer_info': {
                'source_account': 113183203,
                'destination_account': 115471119,
                'amount': 100500,
                'ref_number': 20170227000000000020,
                'bank_ref': 953403
            },
            'request_ref': '2019032202503315569'
        }
        mock_bank_services.return_value = expected_value

        data = {
            "method"         : "IN_HOUSE",
            "source_account" : "113183203",
            "account_no"     : "115471119",
            "amount"         : "100500",
            "email"          : "jennie@blackpink.com",
            "clearing_code"  : "CENAIDJAXXX",
            "address"        : "Jl. Buntu",
            "charge_mode"    : "SOURCE",
        }
        result = BankServices().do_payment(data)
        self.assertEqual(result["transfer_info"]["source_account"],
                         expected_value["transfer_info"]["source_account"])

    @patch.object(BankServices, "interbank_inquiry")
    def test_interbank_inquiry(self, mock_bank_services):
        """ test function that request interbank inquiry"""
        expected_value = {
            'inquiry_info': {
                'account_no': '113183203',
                'account_name': 'DUMMY NAME',
                'transfer_bank_name': 'BCA',
                'transfer_ref': 100000000097
            },
            'request_ref': '2019032203100774022'
        }
        mock_bank_services.return_value = expected_value

        # define required data to execute transfer here
        data = {
            "source_account" : "113183203",
            "bank_code"      : "014",
            "account_no"     : "3333333333",
        }
        result = BankServices().interbank_inquiry(data)
        self.assertEqual(result["inquiry_info"]["account_no"],
                         data["source_account"])

    @patch.object(BankServices, "interbank_payment")
    def test_interbank_payment(self, mock_bank_services):
        """ test function that request interbank inquiry"""
        expected_value = {
            'transfer_info': {
                'account_no': "3333333333",
                'account_name': 'BENEFICIARY NAME',
                'ref_number': 100000000011
            },
            'request_ref': '2019032203280523689'
        }
        mock_bank_services.return_value = expected_value

        # define required data to execute transfer here
        data = {
            "ref_number"     : "20170227000000000020",
            "amount"         : "10000",
            "source_account" : "115471119",
            "account_no"     : "3333333333",
            "account_name"   : "Jennie",
            "bank_code"      : "014",
            "bank_name"      : "BCA",
            "transfer_ref"   : "100000000024",
        }
        result = BankServices().interbank_payment(data)
        self.assertEqual(result["transfer_info"]["account_no"],
                         data["account_no"])
