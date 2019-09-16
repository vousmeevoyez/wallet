"""
    BNI Helper
    _____________________
    this is test case where wallet communicate with BNI VA & COre Banking API
"""
from unittest.mock import Mock, patch

from datetime import datetime

from task.test.base import BaseTestCase

from task.bank.BNI.core.request import BNIOpgAuthRequest
from task.bank.BNI.core.response import BNIOpgAuthResponse
from task.bank.BNI.core.helper import (
    generate_ref_number,
    generate_url,
    authorization,
    CallError,
)


class TestFunction(BaseTestCase):
    def test_generate_ref_number(self):
        result = generate_ref_number()
        self.assertTrue(len(result) > 15)

    def test_generate_url(self):
        result = generate_url("GET_TOKEN")
        self.assertEqual(result, "https://apidev.bni.co.id:8066/api/oauth/token")

        result = generate_url("DO_PAYMENT", "somecooltoken")
        self.assertEqual(
            result,
            "https://apidev.bni.co.id:8066/H2H/v2/dopayment?access_token=somecooltoken",
        )

    @patch("requests.request")
    def test_access_token_required(self, mock_post):
        """ test function to mock success post form request and get access
        token"""
        mock_post.return_value = Mock(status_code=200)

        expected_value = {
            "access_token": "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2",
            "token_type": "Bearer",
            "expires_in": 3599,
            "scope": "resource.WRITE resource.READ",
        }
        mock_post.return_value.json.return_value = expected_value

        result = authorization()
        self.assertEqual(result, expected_value["access_token"])

    def test_access_token_required_failed(self):
        """ test function to mock success post form request and get access
        token"""

        with self.assertRaises(CallError):
            authorization()
