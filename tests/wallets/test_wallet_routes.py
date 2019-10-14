"""
    Integration Testing between wallet & routes
"""
import pytest
import uuid
from unittest.mock import Mock, patch

from app.api.models import (
    User,
    Wallet,
    WalletLock,
    Withdraw,
    IncorrectPin
)
from app.api import db

from tests.reusable.api_list import *


def test_create_wallet(client, setup_user_wallet_va):
    """ CREATE_WALLET CASE 1 : Successfully created wallet """
    access_token, user_id, wallet_id = setup_user_wallet_va

    params = {"label": "wallet label", "pin": "123456"}
    result = create_wallet(client, params, access_token)
    assert result.status_code == 201


def test_create_wallet_serialize_error(client, setup_user_wallet_va):
    """ CREATE_WALLET CASE 3 : Failed created wallet because some invalid payload """
    access_token, user_id, wallet_id = setup_user_wallet_va

    params = {
        "label": "wallet_label",  # ALPHABET ONLY
        "pin": "1",  # PIN TOO SHOORT
    }

    result = create_wallet(client, params, access_token)
    response = result.get_json()
    assert result.status_code == 400
    assert response["error"] == "INVALID_PARAMETER"
    assert response["details"]


def test_get_wallet_info(client, setup_user_wallet_va):
    """ GET_WALLET_INFO CASE 1 : Successfully get wallet information """
    access_token, user_id, wallet_id = setup_user_wallet_va

    result = get_wallet_info(client, wallet_id, access_token)
    response = result.get_json()
    assert response["data"]


def test_remove_wallet(client, setup_user_wallet_va):
    """ REMOVE WALLET CASE 1 : Successfully remove wallet """
    access_token, user_id, wallet_id = setup_user_wallet_va

    result = remove_wallet(client, wallet_id, access_token)
    assert result.status_code == 204


def test_remove_wallet_failed(client, setup_user_wallet_va_without_balance):
    """ REMOVE WALLET CASE 2 : Failed remove wallet because only wallet """
    access_token, user_id, wallet_id = setup_user_wallet_va_without_balance

    result = remove_wallet(client, wallet_id, access_token)
    response = result.get_json()

    assert result.status_code == 422
    assert response["error"] == "ONLY_WALLET"
    assert response["message"]

"""
    GET BALANCE
"""


def test_get_balance(client, setup_user_wallet_va):
    """ GET_BALANCE CASE 1 : return wallet balance information """
    access_token, user_id, wallet_id = setup_user_wallet_va

    result = get_balance(client, wallet_id, access_token)
    response = result.get_json()["data"]
    assert response["id"]

"""
    GET TRANSACTIONS
"""


def test_get_transactions(client, setup_user_wallet_va):
    """ GET TRANSACTIONS CASE 1 : Get wallet transaction for specific date"""
    access_token, user_id, wallet_id = setup_user_wallet_va

    # TEST GETTING IN TRANSACTION
    params = {"start_date": "2019/01/01", "end_date": "2019/01/03", "flag": "IN"}
    result = get_transaction(client, wallet_id, params, access_token)
    response = result.get_json()
    assert result.status_code == 200

    # TEST GETTING OUT TRANSACTION
    params = {"start_date": "2019/01/01", "end_date": "2019/01/03", "flag": "OUT"}
    result = get_transaction(client, wallet_id, params, access_token)
    assert result.status_code == 200

    # TEST GETTING ALL TRANSACTIONS
    params = {"start_date": "2019/01/01", "end_date": "2019/01/03", "flag": "ALL"}
    result = get_transaction(client, wallet_id, params, access_token)
    assert result.status_code == 200


def test_get_transactions_serialize_failed(client, setup_user_wallet_va):
    """ GET TRANSACTIONS CASE 2 : Get wallet transaction with invalid
    payload """
    # TEST GETTING IN TRANSACTION
    access_token, user_id, wallet_id = setup_user_wallet_va

    params = {"start_date": "2019-01-01", "end_date": "2019-01-03", "flag": "KLK"}
    result = get_transaction(client, wallet_id, params, access_token)
    assert result.status_code == 400

"""
    TRANSACTION DETAILS
"""

def test_get_transactions_details_success(client, setup_user_wallet_va,
                                          setup_user_wallet_va_without_balance):
    """ GET TRANSACTIONS DETAILS 1 : Get wallet transaction details but
    transaction not found"""

    source_access_token, source_user_id, source_wallet_id = setup_user_wallet_va
    destination_access_token, destination_user_id, destination_wallet_id = \
        setup_user_wallet_va_without_balance

    params = {
        "amount": "15",
        "notes": "some notes",
        "pin": "123456",
        "types": "PAYROLL",
    }

    result = transfer(client, source_wallet_id, destination_wallet_id, params,
                      source_access_token)
    response = result.get_json()
    assert result.status_code == 202
    assert response["data"]

    params = {"transaction_id": response["data"]["id"]}
    result = get_transaction_details(client, source_wallet_id, params,
                                     source_access_token)
    response = result.get_json()

    assert result.status_code == 200
    assert response["data"]

def test_get_transactions_details_failed(client, setup_user_wallet_va):
    """ GET TRANSACTIONS DETAILS 2 : Get wallet transaction details but
    transaction not found"""
    source_access_token, source_user_id, source_wallet_id = setup_user_wallet_va

    params = {"transaction_id": str(uuid.uuid4())}
    result = get_transaction_details(client, source_wallet_id, params,
                                     source_access_token)
    response = result.get_json()

    assert result.status_code == 404
    assert response["error"] == "TRANSACTION_NOT_FOUND"
    assert response["message"]

"""
    UPDATE PIN
"""

def test_update_pin_incorrect_old_pin(client, setup_user_wallet_va):
    """CASE 1 UPDATE PIN : Incorrect old pin"""
    source_access_token, source_user_id, source_wallet_id = setup_user_wallet_va
    params = {"old_pin": "111111", "pin": "123456", "confirm_pin": "123546"}

    result = update_pin(client, source_wallet_id, params, source_access_token)
    response = result.get_json()
    assert result.status_code == 422
    assert response["error"]

def test_update_pin_unmatch_pin(client, setup_user_wallet_va):
    """ CASE 2 UPDATE PIN : unmatch pin """
    source_access_token, source_user_id, source_wallet_id = setup_user_wallet_va
    params = {"old_pin": "123456", "pin": "123456", "confirm_pin": "123546"}

    result = update_pin(client, source_wallet_id, params, source_access_token)
    assert result.status_code == 422

def test_update_pin_old_pin(client, setup_user_wallet_va):
    """ CASE 3 UPDATE PIN : old pin """
    source_access_token, source_user_id, source_wallet_id = setup_user_wallet_va
    params = {"old_pin": "123456", "pin": "123456", "confirm_pin": "123456"}

    result = update_pin(client, source_wallet_id, params, source_access_token)
    assert result.status_code == 422

"""
    CHECK PIN
"""

def test_check_pin(client, setup_user_wallet_va):
    """CASE 1 CHECK PIN : Check pin successfully"""
    source_access_token, source_user_id, source_wallet_id = setup_user_wallet_va
    params = {"pin": "123456"}

    # clear all lock here
    db.session.query(WalletLock).delete()
    db.session.commit()

    # clear all lock here
    db.session.query(IncorrectPin).delete()
    db.session.commit()

    result = check_pin(client, source_wallet_id, params, source_access_token)
    response = result.get_json()
    assert response["data"]["message"] == "PIN VERIFIED"

def test_check_pin_incorrect(client, setup_user_wallet_va):
    """CASE 2 CHECK PIN : Check pin incorrectly """
    source_access_token, source_user_id, source_wallet_id = setup_user_wallet_va
    params = {"pin": "123452"}

    result = check_pin(client, source_wallet_id, params, source_access_token)
    response = result.get_json()
    assert response["error"] == "INCORRECT_PIN"

    params = {"pin": "123452"}
    result = check_pin(client, source_wallet_id, params, source_access_token)
    response = result.get_json()
    assert response["error"] == "INCORRECT_PIN"

    params = {"pin": "123452"}
    result = check_pin(client, source_wallet_id, params, source_access_token)
    response = result.get_json()
    assert response["error"] == "INCORRECT_PIN"

    params = {"pin": "123452"}
    result = check_pin(client, source_wallet_id, params, source_access_token)
    response = result.get_json()
    assert response["error"] == "MAX_PIN_ATTEMPT"

    # clear all lock here
    db.session.query(WalletLock).delete()
    db.session.commit()

    # clear all lock here
    db.session.query(IncorrectPin).delete()
    db.session.commit()

"""
    QR Code
"""

def test_get_qr(client, setup_user_wallet_va):
    """ GET_QR CASE 1 : return qr string"""
    source_access_token, source_user_id, source_wallet_id = setup_user_wallet_va

    result = get_qr(client, source_wallet_id, source_access_token)
    response = result.get_json()["data"]
    assert result.status_code == 200
    assert response["qr_string"]


def test_qr_checkout(client, setup_user_wallet_va):
    """ QR_CHECKOUT CASE 1 : return user info"""
    source_access_token, source_user_id, source_wallet_id = setup_user_wallet_va

    result = get_qr(client, source_wallet_id, source_access_token)
    response = result.get_json()["data"]
    assert result.status_code == 200
    assert response["qr_string"]

    payload = {"qr_string": response["qr_string"]}

    result = qr_checkout(client, source_wallet_id, payload, source_access_token)
    response = result.get_json()["data"]
    assert result.status_code == 200

"""
    FOrgot pin
"""

def test_forgot_pin(client, setup_user_wallet_va):
    """ FORGOT PIN CASE 1 : send forgot otp"""
    source_access_token, source_user_id, source_wallet_id = setup_user_wallet_va

    result = forgot_pin(client, source_wallet_id, source_access_token)
    response = result.get_json()["data"]

    assert result.status_code == 201
    assert response
    assert response["otp_key"]
    assert response["otp_code"]

    pytest.otp_key = response["otp_key"]
    pytest.otp_code = response["otp_code"]


def test_forgot_pin_pending(client, setup_user_wallet_va):
    """ FORGOT PIN CASE 2 : send forgot otp there's pending """
    source_access_token, source_user_id, source_wallet_id = setup_user_wallet_va

    result = forgot_pin(client, source_wallet_id, source_access_token)
    response = result.get_json()

    assert result.status_code == 422
    assert response["error"] == "PENDING_OTP"

"""
    Verify Forgot OTP
"""

def test_verify_forgot_pin(client, setup_user_wallet_va):
    """ VERIFY FORGOT PIN CASE 1 : verify forgot otp"""
    source_access_token, source_user_id, source_wallet_id = setup_user_wallet_va
    params = {"otp_key": pytest.otp_key, "otp_code": pytest.otp_code, "pin": "12345"}

    result = verify_forgot_pin(client, source_wallet_id, params,
                               source_access_token)
    assert result.status_code == 204

def test_verify_forgot_pin_not_found(client, setup_user_wallet_va):
    """ VERIFY FORGOT PIN CASE 2 : verify forgot otp not found """
    source_access_token, source_user_id, source_wallet_id = setup_user_wallet_va

    params = {"otp_key": "12312312312", "otp_code": "123456", "pin": "12345"}

    result = verify_forgot_pin(client, source_wallet_id, params,
                               source_access_token)
    assert result.status_code == 404

"""
    WITHDRAW
"""

def test_withdraw(client, setup_user_wallet_va_without_balance):
    """ CASE 1 Withdraw : try success withdraw """
    source_access_token, source_user_id, source_wallet_id = \
        setup_user_wallet_va_without_balance

    wallet = Wallet.query.get(source_wallet_id)
    wallet.add_balance(50000)
    db.session.commit()

    params = {"amount": "50000", "pin": "123456"}

    result = withdraw(client, source_wallet_id, params, source_access_token)
    response = result.get_json()["data"]
    assert result.status_code == 200
    assert response["valid_until"]
    assert response["amount"]

    db.session.query(Withdraw).delete()
    db.session.commit()


def test_withdraw_all(client, setup_user_wallet_va_without_balance):
    """ CASE 2 Withdraw : try success withdraw all """
    source_access_token, source_user_id, source_wallet_id = \
        setup_user_wallet_va_without_balance

    wallet = Wallet.query.get(source_wallet_id)
    wallet.add_balance(50000)
    db.session.commit()

    params = {"amount": "0", "pin": "123456"}

    result = withdraw(client, source_wallet_id, params, source_access_token)
    response = result.get_json()["data"]

    assert result.status_code == 200
    assert response["valid_until"]
    assert response["amount"]
