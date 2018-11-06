import sys
import json

sys.path.append("../")
sys.path.append("../app")
sys.path.append("../app/bank")

import unittest
from unittest.mock import Mock, patch

from app            import create_app, db
from app.models     import ApiKey, Wallet, VirtualAccount, Transaction, ExternalLog
from app.bank       import helper
from app.config     import config

class TestConfig(config.Config):
    TESTING = True
    #SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SQLALCHEMY_DATABASE_URI = 'postgresql://modana:password@localhost/unittest_db'

class TestMockEcollectionHelper(unittest.TestCase):

    def setUp(self):
        self.mock_get_patcher = patch("app.bank.utility.remote_call.requests.post")
        self.mock_get         = self.mock_get_patcher.start()

        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        self.mock_get_patcher.stop()

        db.session.remove()
        db.drop_all()
        self.app_context.pop()


    def test_mock_create_va_success(self):
        wallet = Wallet(
        )
        db.session.add(wallet)
        db.session.commit()

        data = {
            "wallet_id"       : wallet.id,
            "amount"          : "1500",
            "customer_name"   : "Jennie",
            "customer_phone"  : "081234123111",
            "datetime_expired": "2019-10-27 00:42:58",
        }

        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "1234", 'virtual_account': "000211" }
        }

        self.mock_get.return_value = Mock()
        self.mock_get.return_value.json.return_value = expected_value

        result = helper.EcollectionHelper().create_va("CREDIT", data)
        self.assertEqual( result["status"], "SUCCESS") # data already existed

    def test_mock_create_va_failed(self):
        wallet = Wallet(
        )
        db.session.add(wallet)
        db.session.commit()

        data = {
            "wallet_id"       : wallet.id,
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

        result = helper.EcollectionHelper().create_va("CREDIT", data)
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

        result = helper.EcollectionHelper().get_inquiry(data)
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

        result = helper.EcollectionHelper().get_inquiry(data)
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

        result = helper.EcollectionHelper().update_va(data)
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

        result = helper.EcollectionHelper().update_va(data)
        self.assertEqual( result["status"], "FAILED")

class TestEcollectionHelper(unittest.TestCase):

    """
    def test_get_inquiry(self):
        data = {
            "trx_id" : "1234",
        }
        result = helper.EcollectionHelper().get_inquiry(data)
        print(result)
        self.assertEqual( result["status"], "SUCCESS")
    #end def
    """

class TestOpgHelper(unittest.TestCase):

    def test_get_token(self):
        #result = helper.OpgHelper().get_token()
        pass
    #end def

if __name__ == "__main__":
    unittest.main(verbosity=2)

