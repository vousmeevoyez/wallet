"""
    Test Withdraw Services
"""
import pytest

from app.api import db

from app.api.models import Wallet, Withdraw

from app.api.wallets.modules.withdraw_services import WithdrawServices

# exceptions
from app.api.error.http import *

from app.api.utility.utils import validate_uuid


""" Test Class for Withdraw Services"""


def test_request_withdraw_success(setup_wallet_info):
    """ test function to request withdraw """
    params = {"amount": 50000, "bank_name": "BNI"}

    result = WithdrawServices(
        setup_wallet_info["id"],
        "123456"
    ).request(params)

    assert result[0]["data"]
    assert result[0]["data"]["virtual_account"]
    assert result[0]["data"]["valid_until"]
    assert result[0]["data"]["amount"] == 50000

    # clear withdraw
    Withdraw.query.filter_by(wallet_id=setup_wallet_info["id"]).delete()


def test_request_withdraw_success_all_amount(setup_wallet_info):
    """ test function to request withdraw with default amount = 0
        if its zero it means we withdraw everything the person have
    """
    params = {"amount": 0, "bank_name": "BNI"}

    result = WithdrawServices(
        setup_wallet_info["id"],
        "123456"
    ).request(params)

    assert result[0]["data"]
    assert result[0]["data"]["virtual_account"]
    assert result[0]["data"]["valid_until"]
    assert result[0]["data"]["amount"] == 100000

    # clear withdraw
    Withdraw.query.filter_by(wallet_id=setup_wallet_info["id"]).delete()


def test_request_withdraw_success_all_amount_max(setup_wallet_info):
    """ test function to request withdraw """
    wallet = Wallet.query.get(setup_wallet_info["id"])
    wallet.add_balance(2500001)
    db.session.commit()

    params = {"amount": 0, "bank_name": "BNI"}

    result = WithdrawServices(
        setup_wallet_info["id"],
        "123456"
    ).request(params)

    assert result[0]["data"]
    assert result[0]["data"]["virtual_account"]
    assert result[0]["data"]["valid_until"]
    assert result[0]["data"]["amount"] == 2500000


def test_request_withdraw_pending(setup_wallet_info):
    """ test function to request withdraw """
    params = {"amount": 50000, "bank_name": "BNI"}

    with pytest.raises(UnprocessableEntity):
        WithdrawServices(setup_wallet_info["id"], "123456").request(params)


def test_request_withdraw_va_already_exist(setup_wallet_info):
    """ test function to request withdraw """
    params = {"amount": 50000, "bank_name": "BNI"}

    db.session.query(Withdraw).delete()
    db.session.commit()

    result = WithdrawServices(
        setup_wallet_info["id"], "123456"
    ).request(params)

    assert result[0]["data"]
    assert result[0]["data"]["virtual_account"]
    assert result[0]["data"]["valid_until"]
    assert result[0]["data"]["amount"] == 50000


def test_request_withdraw_minimal(setup_user_wallet_va):
    """ test function to request withdraw """
    access_token, user_id, wallet_id = setup_user_wallet_va
    params = {"amount": 1000, "bank_name": "BNI"}

    with pytest.raises(UnprocessableEntity):
        WithdrawServices(wallet_id, "123456").request(params)


def test_request_withdraw_max(setup_user_wallet_va):
    """ test function to request withdraw """
    access_token, user_id, wallet_id = setup_user_wallet_va
    params = {"amount": 99999999999999999999, "bank_name": "BNI"}

    with pytest.raises(UnprocessableEntity):
        WithdrawServices(wallet_id, "123456").request(params)


def test_request_withdraw_insufficient(setup_user_wallet_va_without_balance):
    """ test function to request withdraw """

    access_token, user_id, wallet_id = setup_user_wallet_va_without_balance

    params = {"amount": 99999, "bank_name": "BNI"}

    with pytest.raises(UnprocessableEntity):
        WithdrawServices(wallet_id, "123456").request(params)


def test_request_withdraw_incorrect_pin(setup_user_wallet_va_without_balance):
    """ test function to request withdraw """
    access_token, user_id, wallet_id = setup_user_wallet_va_without_balance

    params = {"amount": 99999, "bank_name": "BNI"}

    with pytest.raises(UnprocessableEntity):
        WithdrawServices(wallet_id, "123456").request(params)

    with pytest.raises(UnprocessableEntity):
        WithdrawServices(wallet_id, "123456").request(params)

    with pytest.raises(UnprocessableEntity):
        WithdrawServices(wallet_id, "123456").request(params)

    with pytest.raises(UnprocessableEntity):
        WithdrawServices(wallet_id, "123456").request(params)
