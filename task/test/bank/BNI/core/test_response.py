"""
    Test BNI OPG REsponse
    ______________
"""
from unittest.mock import Mock

from task.test.base import BaseTestCase

from task.bank.BNI.core.response import BNIOpgAuthResponse, BNIOpgResponse
from task.bank.lib.response import (
    InvalidResponseError,
    FailedResponseError,
    ResponseError,
    StatusCodeError,
)


class TestBNIOpgAuthResponse(BaseTestCase):
    def test_to_representation_success(self):
        """ test case wbere BNI VA return success """
        # validate successfull http status code

        expected_data = {
            "access_token": "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2",
            "token_type": "Bearer",
            "expires_in": 3599,
            "scope": "resource.WRITE resource.READ",
        }

        mock_http_response = Mock(status_code=200)

        mock_http_response.json.return_value = expected_data

        response = BNIOpgAuthResponse(mock_http_response).to_representation()
        self.assertEqual(response, expected_data)

    def test_to_representation_failed(self):
        """ test case wbere BNI VA return success """
        # validate successfull http status code

        expected_data = {"error": "unauthorized error"}

        mock_http_response = Mock(status_code=401)

        mock_http_response.json.return_value = expected_data

        with self.assertRaises(ResponseError):
            BNIOpgAuthResponse(mock_http_response).to_representation()


class TestBNIOpgResponse(BaseTestCase):
    def test_to_representation_success(self):
        """ test case wbere BNI OPG return success """
        # validate successfull http status code

        expected_data = {
            "getBalanceResponse": {
                "clientId": "BNISERVICE",
                "parameters": {
                    "responseCode": "0001",
                    "responseMessage": "Request has been processed successfully",
                    "responseTimestamp": "2017-02-24T14:12:25.871Z",
                    "customerName": "Bpk JONOMADE MADEMADEMADEMADE IMAMADE",
                    "accountCurrency": "IDR",
                    "accountBalance": 16732765949981,
                },
            }
        }

        mock_http_response = Mock(status_code=200)

        mock_http_response.json.return_value = expected_data

        response = BNIOpgResponse(mock_http_response).to_representation()
        self.assertEqual(response, expected_data)

    def test_to_representation_failed(self):
        """ test case wbere BNI VA return success """
        # validate successfull http status code

        expected_data = {
            "getBalanceResponse": {
                "clientId": "BNISERVICE",
                "parameters": {
                    "responseCode": "0000",
                    "errorMessage": "Unknown Output",
                    "responseMessage": "Request failed",
                    "responseTimestamp": "2017-02-24T14:12:25.871Z",
                },
            }
        }

        mock_http_response = Mock(status_code=200)

        mock_http_response.json.return_value = expected_data

        with self.assertRaises(ResponseError):
            BNIOpgResponse(mock_http_response).to_representation()
