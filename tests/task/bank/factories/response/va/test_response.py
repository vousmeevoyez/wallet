"""
    Test HTTP Response
    ______________
"""
import pytest

from unittest.mock import Mock, patch

from app.config.external.bank import BNI_ECOLLECTION

from task.bank.lib.helper import encrypt, DecryptError

from task.bank.factories.response.va.response import BNICreditEcollectionResponse
from task.bank.factories.response.va.response import (
    BNICreditEcollectionResponse,
    InvalidResponseError,
    FailedResponseError,
    ResponseError,
)

from tests.reusable.setup import create_http_response


def test_to_representation_success():
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

    mock_http_response = create_http_response(
        200, {"status": "000", "data": encrypted_data}
    )

    response = BNICreditEcollectionResponse()
    response.set(mock_http_response)
    assert response.to_representation() == expected_data


def test_decrypt():
    """ Test case where we try decrypt BNI """

    expected_data = {
        "virtual_account": "988990009912345677",
        "datetime_expired": "2018-10-10T16:00:00+07:00",
    }

    # purposely use random key
    encrypted_data = encrypt("99099", "some-random-secret-key", expected_data)

    response = {"status": "000", "data": encrypted_data}

    mock_http_response = create_http_response(200, response)

    with pytest.raises(InvalidResponseError):
        bni_response = BNICreditEcollectionResponse()
        bni_response.set(mock_http_response)
        bni_response.decrypt(response)

    response = {"status": "000", "data": ""}
    mock_http_response = create_http_response(200, response)

    with pytest.raises(InvalidResponseError):
        bni_response = BNICreditEcollectionResponse()
        bni_response.set(mock_http_response)
        bni_response.decrypt(response)


def test_validate_bni_status():
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
    mock_http_response = create_http_response(200, response)

    bni_response = BNICreditEcollectionResponse()
    bni_response.set(mock_http_response)
    bni_response.validate_bni_status(response)
    assert bni_response.to_representation() == expected_data

    response = {"status": "007", "message": "something ridiculous happen"}
    mock_http_response = create_http_response(200, response)

    with pytest.raises(FailedResponseError):
        bni_response = BNICreditEcollectionResponse()
        bni_response.set(mock_http_response)
        bni_response.validate_bni_status(response)


def test_to_representation_status_error():
    """ Integration method Test case where BNI return error response """

    expected_data = {"status": "001", "message": "Incomplete/invalid Parameter(s)."}

    mock_http_response = create_http_response(200, expected_data)

    with pytest.raises(ResponseError):
        bni_response = BNICreditEcollectionResponse()
        bni_response.set(mock_http_response)
        bni_response.to_representation()
