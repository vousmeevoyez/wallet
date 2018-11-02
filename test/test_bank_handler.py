import sys
import json

sys.path.append("../")
sys.path.append("../app")
sys.path.append("../app/bank")

import unittest
from unittest.mock import Mock, patch

from app.bank import handler

class TestMockEcollectionHandler(unittest.TestCase):

    def setUp(self):
        self.mock_get_patcher = patch("app.bank.utility.remote_call.requests.post")
        self.mock_get         = self.mock_get_patcher.start()

    def tearDown(self):
        self.mock_get_patcher.stop()

    def test_mock_create_va_success(self):
        data = {
            "trx_id"          : "121",
            "amount"          : "1500",
            "customer_name"   : "Jennie",
            "customer_phone"  : "62812341231",
            "virtual_account" : "1230090",
            "datetime_expired": "2019-10-27 00:42:58",
        }

        expected_value = {
            "status" : "000",
            "message" : {'trx_id': data["trx_id"], 'virtual_account': data["virtual_account"] }
        }

        self.mock_get.return_value = Mock()
        self.mock_get.return_value.json.return_value = expected_value

        result = handler.EcollectionHandler().create_va("CREDIT", data)
        self.assertEqual( result["status"], "SUCCESS") # data already existed

    def test_mock_create_va_failed(self):
        data = {
            "trx_id"          : "121",
            "amount"          : "1500",
            "customer_name"   : "Jennie",
            "customer_phone"  : "62812341231",
            "virtual_account" : "1230090",
            "datetime_expired": "2019-10-27 00:42:58",
        }

        expected_value = {
            "status"  : "002",
            "message" : "IP address not allowed or wrong Client ID."
        }

        self.mock_get.return_value = Mock()
        self.mock_get.return_value.json.return_value = expected_value

        result = handler.EcollectionHandler().create_va("CREDIT", data)
        self.assertEqual( result["status"], "FAILED") # data already existed

    def test_mock_get_inquiry_success(self):
        data = {
            "trx_id" : "121",
        }

        expected_value = {
            'status' : '000',
            'message': {'client_id': '99099', 'trx_id': '121', 'virtual_account': '9889909918102605', 'trx_amount': '1', 'customer_name': 'Jennie', 'customer_phone': '', 'customer_email': '', 'datetime_created': '2018-10-26 06:39:27', 'datetime_expired': '2017-10-28 06:39:27', 'datetime_payment': None, 'datetime_last_updated': '2018-10-26 06:43:25', 'payment_ntb': None, 'payment_amount': '0', 'va_status': '2', 'description': '', 'billing_type': 'j', 'datetime_created_iso8601': '2018-10-26T06:39:27+07:00', 'datetime_expired_iso8601': '2017-10-28T06:39:27+07:00', 'datetime_payment_iso8601': None, 'datetime_last_updated_iso8601': '2018-10-26T06:43:25+07:00'
            }
        }

        self.mock_get.return_value = Mock()
        self.mock_get.return_value.json.return_value = expected_value

        result = handler.EcollectionHandler().get_inquiry(data)
        self.assertEqual( result["status"], "SUCCESS")

    def test_mock_get_inquiry_failed(self):
        data = {
            "trx_id"  : "121",
        }

        expected_value = {
            "status"  : "002",
            "message" : "IP address not allowed or wrong Client ID."
        }

        self.mock_get.return_value = Mock()
        self.mock_get.return_value.json.return_value = expected_value

        result = handler.EcollectionHandler().get_inquiry(data)
        self.assertEqual( result["status"], "FAILED")


    def test_mock_update_va_success(self):
        data = {
            "trx_id" : "627493687",
            "amount" : "1000",
            "customer_name"    : "Kelvin",
            "datetime_expired" : "2017-10-29 06:39:27",
        }

        expected_value = {
            "status" : "000",
            "message": {'type': 'updatebilling', 'client_id': '99099', 'trx_id': '627493687', 'trx_amount': '1000', 'customer_name': 'Kelvin', 'datetime_expired': '2017-10-29 06:39:27'}
        }

        self.mock_get.return_value = Mock()
        self.mock_get.return_value.json.return_value = expected_value

        result = handler.EcollectionHandler().update_va(data)
        self.assertEqual( result["status"], "SUCCESS")

    def test_mock_update_va_failed(self):
        data = {
            "trx_id" : "627493687",
            "amount" : "1000",
            "customer_name"    : "Kelvin",
            "datetime_expired" : "2017-10-29 06:39:27",
        }

        expected_value = {
            "status"  : "002",
            "message" : "IP address not allowed or wrong Client ID."
        }

        self.mock_get.return_value = Mock()
        self.mock_get.return_value.json.return_value = expected_value

        result = handler.EcollectionHandler().update_va(data)
        self.assertEqual( result["status"], "FAILED")

class TestEcollectionHandler(unittest.TestCase):

    """
    def test_get_inquiry(self):
        data = {
            "trx_id" : "1234",
        }
        result = handler.EcollectionHandler().get_inquiry(data)
        print(result)
        self.assertEqual( result["status"], "SUCCESS")
    #end def
    """

class TestOpgHandler(unittest.TestCase):

    def test_get_token(self):
        #result = handler.OpgHandler().get_token()
        pass
    #end def

if __name__ == "__main__":
    unittest.main(verbosity=2)

