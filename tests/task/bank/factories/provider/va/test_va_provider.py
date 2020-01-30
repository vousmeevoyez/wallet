import pytest
import json
from datetime import datetime

from unittest.mock import Mock, patch

from task.bank.lib.provider import ProviderError
from task.bank.lib.helper import encrypt
from task.bank.factories.provider.va.provider import BNIVaProvider

from app.config.external.bank import BNI_ECOLLECTION


def encrypt_response(data, types):
    encrypted_data = encrypt(
        BNI_ECOLLECTION[f"{types}_CLIENT_ID"],
        BNI_ECOLLECTION[f"{types}_SECRET_KEY"],
        data,
    )
    return encrypted_data


""" All test case for testing remote call utility"""


@patch("requests.request")
def test_mock_create_va_success(mock_post):
    # payload needed to create virtual account
    data = {
        "trx_id": "1234",
        "amount": "1500",
        "customer_name": "Jennie",
        "customer_phone": "081234123111",
        "expire_date": datetime.now(),
        "account_no": "12345678",
    }

    # expected value from BNI server
    plain_data = {"trx_id": "1234", "virtual_account": "000211"}
    expected_data = {"status": "000", "data": encrypt_response(plain_data, "CREDIT")}

    # replace return value using expected value here
    mock_post.return_value = Mock(status_code=200)
    mock_post.return_value.json.return_value = expected_data

    provider = BNIVaProvider()
    provider.set("CREDIT")
    result = provider.create_va(**data)
    assert result == plain_data


@patch("requests.request")
def test_mock_create_va_failed(mock_post):
    """
        test function to try create va but failed using mock response
        from BNIVaProviderHelper._post
    """
    # payload needed to create a va
    data = {
        "trx_id": "1234",
        "amount": "1500",
        "customer_name": "Jennie",
        "customer_phone": "081234123111",
        "expire_date": datetime.now(),
        "account_no": "12345678",
    }

    # expected value from BNI server
    plain_data = {"trx_id": "1234", "virtual_account": "000211"}
    expected_data = {"status": "001", "message": "my cool error"}

    # replace return value using expected value here
    mock_post.return_value = Mock(status_code=200)
    mock_post.return_value.json.return_value = expected_data

    with pytest.raises(ProviderError):
        provider = BNIVaProvider()
        provider.set("CREDIT")
        provider.create_va(**data)


@patch("requests.request")
def test_mock_create_va_cardless_success(mock_post):
    """
        test function to create cardless va using mock response
        from BNIVaProviderHelper._post
    """
    # required paylod to create va
    data = {
        "amount": "1500",
        "customer_name": "Jennie",
        "customer_phone": "081234123111",
        "expire_date": datetime.now(),
        "account_no": "12345678",
        "trx_id": "12345678",
    }

    # expected value from BNI server
    plain_data = {"trx_id": "12345678", "virtual_account": "000211"}
    expected_data = {"status": "000", "data": encrypt_response(plain_data, "DEBIT")}

    # replace return value using expected value here
    mock_post.return_value = Mock(status_code=200)
    mock_post.return_value.json.return_value = expected_data

    provider = BNIVaProvider()
    provider.set("DEBIT")
    result = provider.create_va(**data)
    assert result == plain_data


@patch("requests.request")
def test_mock_create_va_cardless_failed(mock_post):
    """
        test function to try create cardless va but failed using mock response
        from BNIVaProviderHelper._post
    """
    # required payload to create va
    data = {
        "amount": "1500",
        "customer_name": "Jennie",
        "customer_phone": "081234123111",
        "expire_date": datetime.now(),
        "account_no": "12345678",
        "trx_id": "12345678",
    }

    expected_data = {"status": "001", "message": "my cool error"}

    # replace return value using expected value here
    mock_post.return_value = Mock(status_code=200)
    mock_post.return_value.json.return_value = expected_data

    with pytest.raises(ProviderError):
        provider = BNIVaProvider()
        provider.set("CREDIT")
        provider.create_va(**data)


@patch("requests.request")
def test_mock_get_inquiry_success(mock_post):
    """
        test function to get va inquiry using mock response
        from BNIVaProviderHelper._post
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
            "expire_date": "2017-10-28 06:39:27",
            "datetime_payment": None,
            "datetime_last_updated": "2018-10-26 06:43:25",
            "payment_ntb": None,
            "payment_amount": "0",
            "va_status": "2",
            "description": "",
            "billing_type": "j",
            "datetime_created_iso8601": "2018-10-26T06:39:27+07:00",
            "expire_date_iso8601": "2017-10-28T06:39:27+07:00",
            "datetime_payment_iso8601": None,
            "datetime_last_updated_iso8601": "2018-10-26T06:43:25+07:00",
        },
    }

    expected_data = {"status": "000", "data": encrypt_response(plain_data, "CREDIT")}

    mock_post.return_value = Mock(status_code=200)
    mock_post.return_value.json.return_value = expected_data

    provider = BNIVaProvider()
    provider.set("CREDIT")
    result = provider.get_inquiry("121")
    assert result == plain_data


@patch("requests.request")
def test_mock_get_inquiry_failed(mock_post):
    """
        test function to try get va inquiry but failed using mock response
        from BNIVaProviderHelper._post
    """

    expected_data = {"status": "001", "message": "super cool error"}

    mock_post.return_value = Mock(status_code=200)
    mock_post.return_value.json.return_value = expected_data

    # dummy trx id
    with pytest.raises(ProviderError):
        provider = BNIVaProvider()
        provider.set("CREDIT")
        provider.get_inquiry("123")


@patch("requests.request")
def test_mock_update_va_success(mock_post):
    """
        test function to try update va using mock response
        from BNIVaProviderHelper._post
    """
    data = {
        "trx_id": "627493687",
        "amount": "1000",
        "customer_name": "Kelvin",
        "expire_date": datetime.now(),
    }

    plain_data = {
        "type": "updatebilling",
        "client_id": "99099",
        "trx_id": "627493687",
        "trx_amount": "1000",
        "customer_name": "Kelvin",
        "expire_date": "2017-10-29 06:39:27",
    }

    expected_data = {"status": "000", "data": encrypt_response(plain_data, "CREDIT")}

    mock_post.return_value = Mock(status_code=200)
    mock_post.return_value.json.return_value = expected_data

    provider = BNIVaProvider()
    provider.set("CREDIT")
    result = provider.update_va(**data)
    assert result == plain_data


@patch("requests.request")
def test_mock_update_va_failed(mock_post):
    """
        test function to try update va but falied using mock response
        from BNIVaProviderHelper._post
    """
    data = {
        "trx_id": "627493687",
        "amount": "1000",
        "customer_name": "Kelvin",
        "expire_date": datetime.now(),
    }

    expected_data = {"status": "00`", "message": "my cool error"}

    mock_post.return_value = Mock(status_code=200)
    mock_post.return_value.json.return_value = expected_data

    with pytest.raises(ProviderError):
        provider = BNIVaProvider()
        provider.set("CREDIT")
        provider.update_va(**data)


'''
@patch("requests.request")
def test_health_check_success(mock_post):
    """ test success check to BNI Virtual Account"""
    mock_post.return_value = Mock(status_code=200)
    mock_post.return_value.json.return_value = {
        "status": "009",
        "error": "Unexpected Error",
    }

    result = BNIVaProvider("CREDIT").health_check()
    assert(result, 200)

@patch("requests.request")
def test_health_check_failed(mock_get):
    """ test failed check to BNI Virtual Account"""
    mock_get.side_effect = requests.exceptions.Timeout("error", "errror")

    with pytest.raises(ProviderError):
        BNIVaProvider("CREDIT").health_check()
'''
