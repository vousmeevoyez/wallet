"""
    Test Request Response Factory
    _________________________
"""
import pytest
from datetime import datetime

from task.bank.lib.helper import encrypt, DecryptError

from app.config.external.bank import BNI_ECOLLECTION
from task.bank.factories.factory import generate_request_response
from task.bank.factories.provider.factory import generate_provider

from tests.reusable.setup import create_http_response

def test_create_request_response():
    request, response = generate_request_response("BNI_CREDIT_VA")

    url = "https://apidev.bni.co.id:8066/api/oauth/token"
    method = "POST"
    payload = {"grant_type": "client_credentials"}

    request.url = url
    request.method = method
    request.payload = payload

    print(request.to_representation())

    expected_data = {
        "virtual_account": "988990009912345677",
        "datetime_expired": "2018-10-10T16:00:00+07:00",
    }

    encrypted_data = encrypt(
        BNI_ECOLLECTION["CREDIT_CLIENT_ID"],
        BNI_ECOLLECTION["CREDIT_SECRET_KEY"],
        expected_data,
    )

    mock_http_response = create_http_response(200, {
        "status": "000",
        "data": encrypted_data
    })

    response.set(mock_http_response)

    print(response.to_representation())


def test_va_generate_provider():
    provider = generate_provider("BNI_VA")
    provider.set("CREDIT")
    data = {
        "trx_id": "1234",
        "amount": "1500",
        "customer_name": "Jennie",
        "customer_phone": "081234123111",
        "expire_date": datetime.now(),
        "account_no": "12345678",
    }

    result = provider.create_va(**data)
    print(result)


def test_opg_generate_provider():
    provider = generate_provider("BNI_OPG")
    result = provider.get_balance("123456")
    print(result)
