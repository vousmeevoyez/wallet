"""
    Remote Call
    ______________
"""
from unittest.mock import Mock, patch

from task.test.base import BaseTestCase

from task.bank.lib.request import HTTPRequest

from task.bank.BNI.va.request import (
    BNIEcollectionCreditRequest,
    BNIEcollectionDebitRequest,
)
from task.bank.BNI.va.helper import DecryptError


class TestHTTPRequest(BaseTestCase):
    def test_setup_header(self):
        url = "https://apibeta.bni-ecollection.com/"
        method = "POST"
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

        http_request = HTTPRequest(url=url, method=method)
        http_request.payload = payload
        expected_result = {
            "url": "https://apibeta.bni-ecollection.com/",
            "method": "POST",
            "data": {
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
            },
            "headers": {"Content-Type": "application/json"},
            "timeout": 5,
        }

        self.assertEqual(http_request.to_representation(), expected_result)


class TestBNIEcollectionCreditRequest(BaseTestCase):
    def test_set_payload(self):
        http_request = BNIEcollectionCreditRequest(
            url="https://apibeta.bni-ecollection.com/", method="POST"
        )

        payload = {
            "type": "createbilling",
            "trx_id": "41980682",
            "trx_amount": "100000",
            "billing_type": "d",
            "customer_name": "BL652M",
            "customer_email": "",
            "customer_phone": "628797655047",
            "virtual_account": "9889909667037879",
            "datetime_expired": "2019-09-12 11:45:07",
        }

        http_request.payload = payload

        request = http_request.to_representation()
        # make sure it all has this component
        self.assertTrue(request["url"])
        self.assertTrue(request["method"])
        self.assertTrue(request["headers"])
        self.assertTrue(request["data"])

    def test_get_payload(self):
        http_request = BNIEcollectionCreditRequest(
            url="https://apibeta.bni-ecollection.com/", method="POST"
        )

        payload = {
            "type": "createbilling",
            "trx_id": "41980682",
            "trx_amount": "100000",
            "billing_type": "d",
            "customer_name": "BL652M",
            "customer_email": "",
            "customer_phone": "628797655047",
            "virtual_account": "9889909667037879",
            "datetime_expired": "2019-09-12 11:45:07",
        }

        # set the request here
        http_request.payload = payload
        # get the request here
        request = http_request.payload
        # mandatory information!
        self.assertTrue(request["client_id"])
        self.assertTrue(request["data"])
        # data inside
        request_data = request["data"]
        self.assertTrue(request_data["type"])
        self.assertTrue(request_data["trx_id"])
        self.assertTrue(request_data["trx_amount"])
        self.assertTrue(request_data["billing_type"])
        self.assertTrue(request_data["customer_name"])
        self.assertEqual(request_data["customer_email"], "")
        self.assertEqual(request_data["description"], "")
        self.assertTrue(request_data["customer_phone"])
        self.assertTrue(request_data["virtual_account"])
        self.assertTrue(request_data["datetime_expired"])
        self.assertTrue(request_data["client_id"])


class TestBNIEcollectionDebitRequest(BaseTestCase):
    def test_set_payload(self):
        http_request = BNIEcollectionDebitRequest(
            url="https://apibeta.bni-ecollection.com/", method="POST"
        )

        payload = {
            "type": "createdebitcardless",
            "trx_id": "59061955",
            "trx_amount": "100000",
            "billing_type": "z",
            "customer_name": "5HLRM3",
            "customer_email": "",
            "customer_phone": "628302881349",
            "virtual_account": "9889909655293943",
            "datetime_expired": "2019-09-12 11:45:06",
        }

        http_request.payload = payload

        request = http_request.to_representation()
        # make sure it all has this component
        self.assertTrue(request["url"])
        self.assertTrue(request["method"])
        self.assertTrue(request["headers"])
        self.assertTrue(request["data"])

    def test_get_payload(self):
        http_request = BNIEcollectionDebitRequest(
            url="https://apibeta.bni-ecollection.com/", method="POST"
        )

        payload = {
            "type": "createdebitcardless",
            "trx_id": "59061955",
            "trx_amount": "100000",
            "billing_type": "z",
            "customer_name": "5HLRM3",
            "customer_email": "",
            "customer_phone": "628302881349",
            "virtual_account": "9889909655293943",
            "datetime_expired": "2019-09-12 11:45:06",
        }

        # set the request here
        http_request.payload = payload
        # get the request here
        request = http_request.payload
        # mandatory information!
        self.assertTrue(request["client_id"])
        self.assertTrue(request["data"])
        # data inside
        request_data = request["data"]
        self.assertTrue(request_data["type"])
        self.assertTrue(request_data["trx_id"])
        self.assertTrue(request_data["trx_amount"])
        self.assertTrue(request_data["billing_type"])
        self.assertTrue(request_data["customer_name"])
        self.assertEqual(request_data["customer_email"], "")
        self.assertTrue(request_data["customer_phone"])
        self.assertTrue(request_data["virtual_account"])
        self.assertTrue(request_data["datetime_expired"])
        self.assertTrue(request_data["client_id"])
