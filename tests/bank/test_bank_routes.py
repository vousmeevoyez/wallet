"""
    Bank Routes
"""
from tests.reusable.api_list import *


def test_get_all_banks(client):
    result = get_all_banks(client)
    response = result.get_json()

    assert result.status_code == 200
    assert len(response["data"]) == 164

def test_check_bni_balance_offline(client, setup_admin_token):
    result = check_bni_balance(client, "123456", setup_admin_token)
    response = result.get_json()
    assert result.status_code == 422
    assert response["error"] == "BANK_PROCESS_FAILED"
    assert response["message"] == "TIMEOUT"

def test_check_bni_inquiry_offline(client, setup_admin_token):
    result = check_bni_inquiry(client, "123456", setup_admin_token)
    response = result.get_json()
    assert result.status_code == 422
    assert response["error"] == "BANK_PROCESS_FAILED"
    assert response["message"] == "TIMEOUT"

def test_check_bni_payment_offline(client, setup_admin_token):
    result = check_bni_payment(client, "123456", setup_admin_token)
    response = result.get_json()
    assert result.status_code == 422
    assert response["error"] == "BANK_PROCESS_FAILED"
    assert response["message"] == "TIMEOUT"

def test_bni_do_payment_offline(client, setup_admin_token):
    data = {
        "method": "0",
        "source": "113183203",
        "destination": "115471119",
        "amount": "100500",
        "email": "jennie@blackpink.com",
        "clearing_code": "CENAIDJAXXX",
        "account_name": "Jennie",
        "address": "Jl. Buntu",
        "charge_mode": "OUR",
    }
    result = bni_do_payment(client, data, setup_admin_token)
    response = result.get_json()
    assert result.status_code == 422
    assert response["error"] == "BANK_PROCESS_FAILED"
    assert response["message"] == "TIMEOUT"

def test_bni_interbank_inquiry_offline(client, setup_admin_token):
    data = {
        "source": "113183203",
        "destination": "115471119",
        "bank_code": "014",
    }
    result = bni_interbank_inquiry(client, data, setup_admin_token)
    response = result.get_json()
    assert result.status_code == 422
    assert response["error"] == "BANK_PROCESS_FAILED"
    assert response["message"] == "TIMEOUT"

def test_bni_interbank_payment_offline(client, setup_admin_token):
    data = {
        "amount": "10000",
        "source": "115471119",
        "destination": "3333333333",
        "destination_name": "Jennie",
        "bank_code": "014",
        "bank_name": "BCA",
        "transfer_ref": "100000000024",
    }
    result = bni_interbank_payment(client, data, setup_admin_token)
    response = result.get_json()
    assert result.status_code == 422
    assert response["error"] == "BANK_PROCESS_FAILED"
    assert response["message"] == "TIMEOUT"

