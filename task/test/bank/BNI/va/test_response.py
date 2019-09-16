"""
    Remote Call
    ______________
"""
import json
from unittest.mock import Mock

from app.config.external.bank import BNI_ECOLLECTION

from task.test.base import BaseTestCase

from task.bank.BNI.va.helper import encrypt, DecryptError

from task.bank.BNI.va.response import (
    BNIEcollectionCreditResponse,
    BNIEcollectionDebitResponse,
)
from task.bank.lib.response import (
    HTTPResponse,
    InvalidResponseError,
    FailedResponseError,
    StatusCodeError,
    ResponseError,
)


class TestHTTPResponse(BaseTestCase):
    def test_validate_success_status_code(self):
        # validate successfull http status code
        mock_http_response = Mock(status_code=200)

        response = HTTPResponse(mock_http_response)
        self.assertTrue(response.validate_status_code())

    def test_validate_failed_status_code(self):
        # first test error http code with JSON
        mock_http_response = Mock(status_code=400)

        with self.assertRaises(StatusCodeError):
            HTTPResponse(mock_http_response).validate_status_code()

        mock_http_response = Mock(status_code=200)

        result = HTTPResponse(mock_http_response).validate_status_code()
        self.assertTrue(result)

    def test_extract(self):

        data = {"data": "wow things"}

        extracted = HTTPResponse._extract(data)
        self.assertEqual(extracted, "wow things")

        data = {"wow things"}

        extracted = HTTPResponse._extract(data)
        self.assertEqual(extracted, {"wow things"})

        data = "wow things"

        extracted = HTTPResponse._extract(data)
        self.assertEqual(extracted, "wow things")

        data = {"data": {"data": "cool inside"}}
        extracted = HTTPResponse._extract(data)
        self.assertEqual(extracted, {"data": "cool inside"})

    def test_validate_data(self):
        mock_http_response = Mock()

        mock_http_response.json.return_value = {
            "data": "Your request has been processsed successfully"
        }

        response = HTTPResponse(mock_http_response).validate_data()
        self.assertTrue(response)

        mock_http_response = Mock()

        mock_http_response.json.return_value = "request success"
        response = HTTPResponse(mock_http_response).validate_data()
        self.assertTrue(response)

        mock_http_response = Mock()

        # simujlate error parsing json
        mock_http_response.json.side_effect = ValueError

        with self.assertRaises(InvalidResponseError):
            response = HTTPResponse(mock_http_response).validate_data()

    def test_to_representation_ok(self):
        """ test successfull request """
        mock_http_response = Mock(status_code=200)
        expected_data = {"data": "Your request has been processed successfully"}
        mock_http_response.json.return_value = expected_data

        response = HTTPResponse(mock_http_response).to_representation()
        self.assertEqual(response, expected_data)

    def test_to_representation_bad_request(self):
        """ test successfull request """
        mock_http_response = Mock(status_code=400)
        expected_data = {"error": "some bad request"}
        mock_http_response.json.return_value = expected_data

        with self.assertRaises(StatusCodeError):
            HTTPResponse(response=mock_http_response).to_representation()

    def test_to_representation_internal_error(self):
        """ test successfull request """
        mock_http_response = Mock(status_code=500)
        expected_data = {"error": "internal server error"}
        mock_http_response.json.return_value = expected_data

        with self.assertRaises(StatusCodeError):
            HTTPResponse(response=mock_http_response).to_representation()


class TestBNIEcollectionCreditResponse(BaseTestCase):
    def test_to_representation_success(self):
        """ test case wbere BNI VA return success """
        # validate successfull http status code

        expected_data = {
            "virtual_account": "988990009912345677",
            "datetime_expired": "2018-10-10T16:00:00+07:00",
        }

        encrypted_data = encrypt(
            BNI_ECOLLECTION["CREDIT_CLIENT_ID"],
            BNI_ECOLLECTION["CREDIT_SECRET_KEY"],
            expected_data,
        )

        mock_http_response = Mock(status_code=200)
        mock_http_response.json.return_value = {"status": "000", "data": encrypted_data}

        response = BNIEcollectionCreditResponse(mock_http_response).to_representation()
        self.assertEqual(response, expected_data)

    def test_decrypt(self):
        """ Test case where we try decrypt BNI """

        expected_data = {
            "virtual_account": "988990009912345677",
            "datetime_expired": "2018-10-10T16:00:00+07:00",
        }

        # purposely use debit to raise error
        encrypted_data = encrypt(
            BNI_ECOLLECTION["DEBIT_CLIENT_ID"],
            BNI_ECOLLECTION["DEBIT_SECRET_KEY"],
            expected_data,
        )

        http_response = Mock(status_code=200)

        response = {"status": "000", "data": encrypted_data}

        with self.assertRaises(InvalidResponseError):
            BNIEcollectionCreditResponse(http_response).decrypt(response)

        response = {"status": "000", "data": ""}

        with self.assertRaises(InvalidResponseError):
            BNIEcollectionCreditResponse(http_response).decrypt(response)

    def test_validate_bni_status(self):
        """ Test case where we try validate BNI response status """

        expected_data = {
            "virtual_account": "988990009912345677",
            "datetime_expired": "2018-10-10T16:00:00+07:00",
        }

        # purposely use debit to raise error
        encrypted_data = encrypt(
            BNI_ECOLLECTION["CREDIT_CLIENT_ID"],
            BNI_ECOLLECTION["CREDIT_SECRET_KEY"],
            expected_data,
        )

        response = {"status": "000", "data": encrypted_data}

        result = BNIEcollectionCreditResponse.validate_bni_status(response)
        self.assertEqual(result, response)

        response = {"status": "007", "message": "something ridiculous happen"}

        with self.assertRaises(FailedResponseError):
            result = BNIEcollectionCreditResponse.validate_bni_status(response)

    def test_to_representation_status_error(self):
        """ Integration method Test case where BNI return error response """

        expected_data = {"status": "001", "message": "Incomplete/invalid Parameter(s)."}

        mock_http_response = Mock(status_code=200)
        mock_http_response.json.return_value = expected_data

        with self.assertRaises(ResponseError):
            BNIEcollectionCreditResponse(mock_http_response).to_representation()

    def test_to_representation_decrypt_error(self):
        """ intehgration method Test case where we received invalid decrpyt
        response """

        expected_data = {
            "virtual_account": "988990009912345677",
            "datetime_expired": "2018-10-10T16:00:00+07:00",
        }

        # purposely use debit to raise error
        encrypted_data = encrypt(
            BNI_ECOLLECTION["DEBIT_CLIENT_ID"],
            BNI_ECOLLECTION["DEBIT_SECRET_KEY"],
            expected_data,
        )

        mock_http_response = Mock(status_code=200)
        mock_http_response.json.return_value = {"status": "000", "data": encrypted_data}

        with self.assertRaises(ResponseError):
            BNIEcollectionCreditResponse(mock_http_response).to_representation()


class TestBNIEcollectionDebitResponse(BaseTestCase):
    def test_to_representation_success(self):
        """ test case wbere BNI VA return success """
        # validate successfull http status code

        expected_data = {
            "virtual_account": "988990009912345677",
            "datetime_expired": "200018-1000-1000T16:000000:000000+0007:000000",
        }

        encrypted_data = encrypt(
            BNI_ECOLLECTION["DEBIT_CLIENT_ID"],
            BNI_ECOLLECTION["DEBIT_SECRET_KEY"],
            expected_data,
        )

        mock_http_response = Mock(status_code=200)
        mock_http_response.json.return_value = {"status": "000", "data": encrypted_data}

        response = BNIEcollectionDebitResponse(mock_http_response).to_representation()
        self.assertEqual(response, expected_data)

    def test_decrypt(self):
        """ Test case where we try decrypt BNI """

        expected_data = {
            "virtual_account": "988990009912345677",
            "datetime_expired": "200018-1000-1000T16:000000:000000+0007:000000",
        }

        # purposely use debit to raise error
        encrypted_data = encrypt(
            BNI_ECOLLECTION["CREDIT_CLIENT_ID"],
            BNI_ECOLLECTION["CREDIT_SECRET_KEY"],
            expected_data,
        )

        http_response = Mock(status_code=200)

        response = {"status": "000", "data": encrypted_data}

        with self.assertRaises(InvalidResponseError):
            BNIEcollectionDebitResponse(http_response).decrypt(response)

        response = {"status": "000", "data": ""}

        with self.assertRaises(InvalidResponseError):
            BNIEcollectionDebitResponse(http_response).decrypt(response)

    def test_validate_bni_status(self):
        """ Test case where we try validate BNI response status """

        expected_data = {
            "virtual_account": "988990009912345677",
            "datetime_expired": "200018-1000-1000T16:000000:000000+0007:000000",
        }

        # purposely use debit to raise error
        encrypted_data = encrypt(
            BNI_ECOLLECTION["DEBIT_CLIENT_ID"],
            BNI_ECOLLECTION["DEBIT_SECRET_KEY"],
            expected_data,
        )

        response = {"status": "000", "data": encrypted_data}

        result = BNIEcollectionDebitResponse.validate_bni_status(response)
        self.assertEqual(result, response)

        response = {"status": "0000007", "message": "something ridiculous happen"}

        with self.assertRaises(FailedResponseError):
            result = BNIEcollectionDebitResponse.validate_bni_status(response)

    def test_to_representation_status_error(self):
        """ Integration method Test case where BNI return error response """

        expected_data = {
            "status": "0000001",
            "message": "Incomplete/invalid Parameter(s).",
        }

        mock_http_response = Mock(status_code=200)
        mock_http_response.json.return_value = expected_data

        with self.assertRaises(ResponseError):
            BNIEcollectionDebitResponse(mock_http_response).to_representation()

    def test_to_representation_decrypt_error(self):
        """ intehgration method Test case where we received invalid decrpyt
        response """

        expected_data = {
            "virtual_account": "988990009912345677",
            "datetime_expired": "200018-1000-1000T16:000000:000000+0007:000000",
        }

        # purposely use debit to raise error
        encrypted_data = encrypt(
            BNI_ECOLLECTION["CREDIT_CLIENT_ID"],
            BNI_ECOLLECTION["CREDIT_SECRET_KEY"],
            expected_data,
        )

        mock_http_response = Mock(status_code=200)
        mock_http_response.json.return_value = {"status": "000", "data": encrypted_data}

        with self.assertRaises(ResponseError):
            BNIEcollectionDebitResponse(mock_http_response).to_representation()
