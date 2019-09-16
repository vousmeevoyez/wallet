"""
    Test Services
    ______________
    test communication module
"""
from datetime import datetime
import requests
import json

from unittest.mock import Mock, patch

from task.test.base import BaseTestCase
from task.bank.BNI.va.services import VirtualAccount, RequestError, ApiError
from task.bank.BNI.va.BniEnc3 import BniEnc

from app.config.external.bank import BNI_ECOLLECTION


def encrypt_response(data, types):
    encrypted_data = (
        BniEnc()
        .encrypt(
            json.dumps(data),
            BNI_ECOLLECTION[f"{types}_CLIENT_ID"],
            BNI_ECOLLECTION[f"{types}_SECRET_KEY"],
        )
        .decode("utf-8")
    )
    return encrypted_data


class TestMockVirtualAccountServices(BaseTestCase):
    """ All test case for testing remote call utility"""

    @patch("requests.request")
    def test_post_success(self, mock_post):
        """ test success post request to BNI VA API"""
        # bni payload
        payload = {
            "type": "createbilling",
            "client_id": "99099",
            "trx_id": "12345",
            "trx_amount": "100",
            "billing_type": "j",
            "customer_name": "Kelvin",
            "customer_email": "",
            "customer_phone": "",
            "virtual_account": "",
            "datetime_expired": "",
            "description": "",
        }

        expected_data = {
            "virtual_account": "9889909912345677",
            "datetime_expired": "2018-10-10T16:00:00+07:00",
        }

        mock_post.return_value = Mock(status_code=200)
        mock_post.return_value.json.return_value = {
            "status": "000",
            "data": encrypt_response(expected_data, "CREDIT"),
        }

        result = VirtualAccount("CREDIT")._post(payload)
        self.assertEqual(result, expected_data)

    @patch("requests.request")
    def test_post_failed(self, mock_post):
        """ test failed post request to BNI VA API"""
        # bni payload
        payload = {
            "type": "createbilling",
            "client_id": "99099",
            "trx_id": "12345",
            "trx_amount": "100",
            "billing_type": "j",
            "customer_name": "Kelvin",
            "customer_email": "",
            "customer_phone": "",
            "virtual_account": "",
            "datetime_expired": "",
            "description": "",
        }

        expected_data = {"status": "001", "message": "Incomplete/invalid Parameter(s)."}

        mock_post.return_value = Mock(status_code=200)
        mock_post.return_value.json.return_value = expected_data

        with self.assertRaises(RequestError):
            VirtualAccount("CREDIT")._post(payload)

    @patch("requests.request")
    def test_post_timeout(self, mock_post):
        """ test failed post request to BNI VA API"""
        # bni payload
        payload = {
            "type": "createbilling",
            "client_id": "99099",
            "trx_id": "12345",
            "trx_amount": "100",
            "billing_type": "j",
            "customer_name": "Kelvin",
            "customer_email": "",
            "customer_phone": "",
            "virtual_account": "",
            "datetime_expired": "",
            "description": "",
        }

        mock_post.side_effect = requests.exceptions.Timeout

        with self.assertRaises(RequestError):
            VirtualAccount("CREDIT")._post(payload)

    @patch("requests.request")
    def test_mock_create_va_success(self, mock_post):
        """
            test function to successfully create va using mock response
            from VirtualAccountHelper._post
        """

        # payload needed to create virtual account
        data = {
            "amount": "1500",
            "customer_name": "Jennie",
            "customer_phone": "081234123111",
            "datetime_expired": datetime.now(),
            "virtual_account": "12345678",
            "transaction_id": "12345678",
        }

        # expected value from BNI server
        plain_data = {"trx_id": "1234", "virtual_account": "000211"}
        expected_data = {
            "status": "000",
            "data": encrypt_response(plain_data, "CREDIT"),
        }

        # replace return value using expected value here
        mock_post.return_value = Mock(status_code=200)
        mock_post.return_value.json.return_value = expected_data

        result = VirtualAccount("CREDIT").create_va(data)
        self.assertEqual(result, plain_data)

    @patch("requests.request")
    def test_mock_create_va_failed(self, mock_post):
        """
            test function to try create va but failed using mock response
            from VirtualAccountHelper._post
        """
        # payload needed to create a va
        data = {
            "amount": "1500",
            "customer_name": "Jennie",
            "customer_phone": "081234123111",
            "datetime_expired": datetime.now(),
            "virtual_account": "12345678",
            "transaction_id": "12345678",
        }

        expected_data = {"status": "001", "message": "my cool error"}

        # replace return value using expected value here
        mock_post.return_value = Mock(status_code=200)
        mock_post.return_value.json.return_value = expected_data

        with self.assertRaises(ApiError):
            VirtualAccount("CREDIT").create_va(data)

    @patch("requests.request")
    def test_mock_create_va_cardless_success(self, mock_post):
        """
            test function to create cardless va using mock response
            from VirtualAccountHelper._post
        """
        # required paylod to create va
        data = {
            "amount": "1500",
            "customer_name": "Jennie",
            "customer_phone": "081234123111",
            "datetime_expired": datetime.now(),
            "virtual_account": "12345678",
            "transaction_id": "12345678",
        }

        # expected value from BNI server
        plain_data = {"trx_id": "1234", "virtual_account": "000211"}
        expected_data = {"status": "000", "data": encrypt_response(plain_data, "DEBIT")}

        # replace return value using expected value here
        mock_post.return_value = Mock(status_code=200)
        mock_post.return_value.json.return_value = expected_data

        result = VirtualAccount("DEBIT").create_va(data)
        self.assertEqual(result, plain_data)  # data already existed

    @patch("requests.request")
    def test_mock_create_va_cardless_failed(self, mock_post):
        """
            test function to try create cardless va but failed using mock response
            from VirtualAccountHelper._post
        """
        # required payload to create va
        data = {
            "amount": "1500",
            "customer_name": "Jennie",
            "customer_phone": "081234123111",
            "datetime_expired": datetime.now(),
            "virtual_account": "12345678",
            "transaction_id": "12345678",
        }

        expected_data = {"status": "001", "message": "my cool error"}

        # replace return value using expected value here
        mock_post.return_value = Mock(status_code=200)
        mock_post.return_value.json.return_value = expected_data

        with self.assertRaises(ApiError):
            VirtualAccount("DEBIT").create_va(data)

    @patch("requests.request")
    def test_mock_get_inquiry_success(self, mock_post):
        """
            test function to get va inquiry using mock response
            from VirtualAccountHelper._post
        """

        # expected_value from bni server
        plain_data = {
            "status": "000",
            "data": {
                "client_id": "99099",
                "trx_id": "121",
                "virtual_account": "9889909918102605",
                "trx_amount": "1",
                "customer_name": "Jennie",
                "customer_phone": "",
                "customer_email": "",
                "datetime_created": "2018-10-26 06:39:27",
                "datetime_expired": "2017-10-28 06:39:27",
                "datetime_payment": None,
                "datetime_last_updated": "2018-10-26 06:43:25",
                "payment_ntb": None,
                "payment_amount": "0",
                "va_status": "2",
                "description": "",
                "billing_type": "j",
                "datetime_created_iso8601": "2018-10-26T06:39:27+07:00",
                "datetime_expired_iso8601": "2017-10-28T06:39:27+07:00",
                "datetime_payment_iso8601": None,
                "datetime_last_updated_iso8601": "2018-10-26T06:43:25+07:00",
            },
        }

        expected_data = {
            "status": "000",
            "data": encrypt_response(plain_data, "CREDIT"),
        }

        mock_post.return_value = Mock(status_code=200)
        mock_post.return_value.json.return_value = expected_data

        result = VirtualAccount("CREDIT").get_inquiry("121")
        self.assertEqual(result, plain_data)

    @patch("requests.request")
    def test_mock_get_inquiry_failed(self, mock_post):
        """
            test function to try get va inquiry but failed using mock response
            from VirtualAccountHelper._post
        """

        expected_data = {"status": "001", "message": "super cool error"}

        mock_post.return_value = Mock(status_code=200)
        mock_post.return_value.json.return_value = expected_data

        # dummy trx id
        with self.assertRaises(ApiError):
            VirtualAccount("CREDIT").get_inquiry("123")

    @patch("requests.request")
    def test_mock_update_va_success(self, mock_post):
        """
            test function to try update va using mock response
            from VirtualAccountHelper._post
        """
        data = {
            "trx_id": "627493687",
            "amount": "1000",
            "customer_name": "Kelvin",
            "datetime_expired": datetime.now(),
        }

        plain_data = {
            "type": "updatebilling",
            "client_id": "99099",
            "trx_id": "627493687",
            "trx_amount": "1000",
            "customer_name": "Kelvin",
            "datetime_expired": "2017-10-29 06:39:27",
        }

        expected_data = {
            "status": "000",
            "data": encrypt_response(plain_data, "CREDIT"),
        }

        mock_post.return_value = Mock(status_code=200)
        mock_post.return_value.json.return_value = expected_data

        result = VirtualAccount("CREDIT").update_va(data)
        self.assertEqual(result, plain_data)

    @patch("requests.request")
    def test_mock_update_va_failed(self, mock_post):
        """
            test function to try update va but falied using mock response
            from VirtualAccountHelper._post
        """
        data = {
            "trx_id": "627493687",
            "amount": "1000",
            "customer_name": "Kelvin",
            "datetime_expired": datetime.now(),
        }

        expected_data = {"status": "00`", "message": "my cool error"}

        mock_post.return_value = Mock(status_code=200)
        mock_post.return_value.json.return_value = expected_data

        with self.assertRaises(ApiError):
            VirtualAccount("CREDIT").update_va(data)

    @patch("requests.request")
    def test_post_credit_failed(self, mock_post):
        """ test failed post function to BNI Credit E-Collection"""
        payload = {
            "client_id": "99099",
            "trx_id": "121",
            "virtual_account": "9889909918102605",
            "trx_amount": "1",
            "customer_name": "Jennie",
            "customer_phone": "",
            "customer_email": "",
            "datetime_expired": "2017-10-28 06:39:27",
            "va_status": "2",
            "description": "",
            "billing_type": "j",
        }

        expected_data = {
            "virtual_account": "9889909912345677",
            "datetime_expired": "2018-10-10T16:00:00+07:00",
        }

        mock_post.return_value = Mock(status_code=200)
        mock_post.return_value.json.return_value = {
            "status": "000",
            "data": encrypt_response(expected_data, "CREDIT"),
        }

        result = VirtualAccount("CREDIT")._post(payload)
        self.assertEqual(result, expected_data)

    @patch("requests.request")
    def test_health_check_success(self, mock_post):
        """ test success check to BNI Virtual Account"""
        mock_post.return_value = Mock(status_code=200)
        mock_post.return_value.json.return_value = {
            "status": "009",
            "error": "Unexpected Error",
        }

        result = VirtualAccount.health_check()
        self.assertEqual(result, 200)

    @patch("requests.request")
    def test_health_check_failed(self, mock_get):
        """ test failed check to BNI Virtual Account"""
        mock_get.side_effect = requests.exceptions.Timeout("error", "errror")

        with self.assertRaises(ApiError):
            VirtualAccount.health_check()
