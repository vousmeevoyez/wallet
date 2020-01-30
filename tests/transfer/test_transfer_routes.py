"""
    Test Transfer Routes
"""
import uuid
from unittest.mock import Mock, patch

from tests.reusable.api_list import *

from app.api import db
from app.api.models import Wallet, IncorrectPin

"""
    TRANSFER
"""


def test_transfer(client, setup_user_wallet_va, setup_user_wallet_va_without_balance):
    """ CASE 1 Transfer : successfully transfer """
    # inject balance
    source_access_token, source_user_id, source_wallet_id = setup_user_wallet_va
    destination_access_token, destination_user_id, destination_wallet_id = (
        setup_user_wallet_va_without_balance
    )

    params = {
        "amount": "15",
        "notes": "some notes",
        "pin": "123456",
        "types": "PAYROLL",
    }

    result = transfer(
        client, source_wallet_id, destination_wallet_id, params, source_access_token
    )
    response = result.get_json()
    assert result.status_code == 202
    assert response["data"]["id"]


def test_transfer_invalid_destination(
    client, setup_user_wallet_va, setup_user_wallet_va_without_balance
):
    """ CASE 2 Transfer : try transfer with same between source """

    source_access_token, source_user_id, source_wallet_id = setup_user_wallet_va
    destination_access_token, destination_user_id, destination_wallet_id = (
        setup_user_wallet_va_without_balance
    )

    params = {
        "amount": "15",
        "types": "PAYROLL",
        "notes": "some notes",
        "pin": "123456",
    }

    result = transfer(
        client, source_wallet_id, source_wallet_id, params, source_access_token
    )
    response = result.get_json()
    assert result.status_code == 422
    assert response["error"] == "INVALID_DESTINATION"


def test_transfer_locked_source(
    client, setup_user_wallet_va, setup_user_wallet_va_without_balance
):
    """ CASE 3 Transfer : but wallet is locked"""

    source_access_token, source_user_id, source_wallet_id = setup_user_wallet_va
    destination_access_token, destination_user_id, destination_wallet_id = (
        setup_user_wallet_va_without_balance
    )

    # lock wallet
    wallet = Wallet.query.get(source_wallet_id)
    wallet.lock()
    db.session.commit()

    params = {
        "amount": "15",
        "types": "PAYROLL",
        "notes": "some notes",
        "pin": "123456",
    }

    result = transfer(
        client, source_wallet_id, destination_wallet_id, params, source_access_token
    )
    response = result.get_json()
    assert result.status_code == 422
    assert response["error"] == "WALLET_LOCKED"

    # unlock wallet
    wallet = Wallet.query.get(source_wallet_id)
    wallet.unlock()
    db.session.commit()


def test_transfer_incorrect_pin(
    client, setup_user_wallet_va, setup_user_wallet_va_without_balance
):
    """ CASE 4 Transfer : try transfer with invalid pin"""
    # clear any incorrect attempt
    IncorrectPin.query.filter().delete()

    source_access_token, source_user_id, source_wallet_id = setup_user_wallet_va
    destination_access_token, destination_user_id, destination_wallet_id = (
        setup_user_wallet_va_without_balance
    )

    params = {
        "amount": "15",
        "types": "PAYROLL",
        "notes": "some notes",
        "pin": "111111",
    }

    # first attempt
    result = transfer(
        client, source_wallet_id, destination_wallet_id, params, source_access_token
    )
    response = result.get_json()
    assert result.status_code == 422
    assert response["error"] == "INCORRECT_PIN"

    # second attempt
    result = transfer(
        client, source_wallet_id, destination_wallet_id, params, source_access_token
    )
    response = result.get_json()
    assert result.status_code == 422
    assert response["error"] == "INCORRECT_PIN"

    # third attempt
    result = transfer(
        client, source_wallet_id, destination_wallet_id, params, source_access_token
    )
    response = result.get_json()
    assert result.status_code == 422
    assert response["error"] == "INCORRECT_PIN"

    # fourth attempt
    result = transfer(
        client, source_wallet_id, destination_wallet_id, params, source_access_token
    )
    response = result.get_json()
    assert result.status_code == 422
    assert response["error"] == "MAX_PIN_ATTEMPT"

    # fifth attempt
    result = transfer(
        client, source_wallet_id, destination_wallet_id, params, source_access_token
    )
    response = result.get_json()
    assert result.status_code == 422
    assert response["error"] == "WALLET_LOCKED"

    # unlock wallet
    wallet = Wallet.query.get(source_wallet_id)
    wallet.unlock()
    db.session.commit()

    # clear any incorrect attempt
    IncorrectPin.query.filter().delete()


"""
    BANK TRANSFER
"""


def test_bank_transfer(client, setup_user_wallet_va_bank_acc):
    """ CASE 1 Bank Transfer : successfully bank transfer """
    access_token, user_id, wallet_id, bank_acc_id = setup_user_wallet_va_bank_acc

    params = {"amount": "15", "notes": "some notes", "pin": "123456"}
    result = bank_transfer(client, wallet_id, bank_acc_id, params, access_token)
    response = result.get_json()["data"]
    assert result.status_code == 202
    assert response["id"]


def test_bank_transfer_bank_account_not_found(client, setup_user_wallet_va_bank_acc):
    """ CASE 2 Bank Transfer invalid bank account id: successfully bank transfer """
    access_token, user_id, wallet_id, bank_acc_id = setup_user_wallet_va_bank_acc

    params = {"amount": "15", "notes": "some notes", "pin": "123456"}
    result = bank_transfer(client, wallet_id, str(uuid.uuid4()), params, access_token)
    assert result.status_code == 404


############ PATCH #################
def test_bank_transfer_api_key(client, setup_user_wallet_va_bank_acc):
    """ CASE 1 Bank Transfer : successfully bank transfer """
    access_token, user_id, wallet_id, bank_acc_id = setup_user_wallet_va_bank_acc

    params = {"amount": "15", "notes": "some notes", "pin": "123456"}

    # api key
    _api_key = "8c574c41-3e01-4763-89af-fd370989da33"

    result = bank_transfer2(client, wallet_id, bank_acc_id, params, _api_key)
    response = result.get_json()["data"]

    assert result.status_code == 202
    assert response["id"]
