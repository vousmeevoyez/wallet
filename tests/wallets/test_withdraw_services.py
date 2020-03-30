"""
    Test Withdraw Services
"""
import pytest

from app.api import db

from app.api.models import Wallet, Withdraw, VirtualAccount

from app.api.wallets.modules.withdraw_services import WithdrawServices

# exceptions
from app.lib.http_error import *

from app.api.utility.utils import validate_uuid


""" Test Class for Withdraw Services"""


def test_request_withdraw_success(setup_wallet_info):
    """ test function to request successful withdraw """
    params = {"amount": 50000, "bank_code": "009"}

    result = WithdrawServices(setup_wallet_info["id"], "123456").request(params)

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
    params = {"amount": 0, "bank_code": "009"}

    result = WithdrawServices(setup_wallet_info["id"], "123456").request(params)

    assert result[0]["data"]
    assert result[0]["data"]["virtual_account"]
    assert result[0]["data"]["valid_until"]
    assert result[0]["data"]["amount"] == 100000

    # clear withdraw
    Withdraw.query.filter_by(wallet_id=setup_wallet_info["id"]).delete()


def test_request_withdraw_success_all_amount_max(setup_wallet_info):
    """ test function to request withdraw all amount max but allowed max is
    only 2.5 mio
    """
    wallet = Wallet.query.get(setup_wallet_info["id"])
    wallet.add_balance(2500001)
    db.session.commit()

    params = {"amount": 0, "bank_code": "009"}

    result = WithdrawServices(setup_wallet_info["id"], "123456").request(params)

    assert result[0]["data"]
    assert result[0]["data"]["virtual_account"]
    assert result[0]["data"]["valid_until"]
    assert result[0]["data"]["amount"] == 2500000


def test_request_withdraw_pending(setup_wallet_info):
    """ test function to request withdraw but already request in process """
    params = {"amount": 50000, "bank_code": "009"}

    with pytest.raises(UnprocessableEntity):
        WithdrawServices(setup_wallet_info["id"], "123456").request(params)


def test_request_withdraw_va_already_exist(setup_wallet_info):
    """ test function to request withdraw but va already created before it
    means we just need to reactive (create new va with same number but
    different trx id )"""
    params = {"amount": 50000, "bank_code": "009"}

    # clear any previous withdraw
    db.session.query(Withdraw).delete()
    db.session.commit()
    # add virtual account information
    va = VirtualAccount.query.filter_by(wallet_id=setup_wallet_info["id"]).all()
    for v in va:
        v.status = 1
        db.session.commit()

    result = WithdrawServices(setup_wallet_info["id"], "123456").request(params)

    assert result[0]["data"]
    assert result[0]["data"]["virtual_account"]
    assert result[0]["data"]["valid_until"]
    assert result[0]["data"]["amount"] == 50000


def test_request_withdraw_minimal(setup_user_wallet_va):
    """ test function to request withdraw """
    access_token, user_id, wallet_id = setup_user_wallet_va
    params = {"amount": 1000, "bank_code": "009"}

    with pytest.raises(UnprocessableEntity):
        WithdrawServices(wallet_id, "123456").request(params)


def test_request_withdraw_max(setup_user_wallet_va):
    """ test function to request withdraw """
    access_token, user_id, wallet_id = setup_user_wallet_va
    params = {"amount": 99999999999999999999, "bank_code": "009"}

    with pytest.raises(UnprocessableEntity):
        WithdrawServices(wallet_id, "123456").request(params)


def test_request_withdraw_insufficient(setup_user_wallet_va_without_balance):
    """ test function to request withdraw """

    access_token, user_id, wallet_id = setup_user_wallet_va_without_balance

    params = {"amount": 99999, "bank_code": "009"}

    with pytest.raises(UnprocessableEntity):
        WithdrawServices(wallet_id, "123456").request(params)


def test_request_withdraw_incorrect_pin(setup_user_wallet_va_without_balance):
    """ test function to request withdraw """
    access_token, user_id, wallet_id = setup_user_wallet_va_without_balance

    params = {"amount": 99999, "bank_code": "009"}

    with pytest.raises(UnprocessableEntity):
        WithdrawServices(wallet_id, "123456").request(params)

    with pytest.raises(UnprocessableEntity):
        WithdrawServices(wallet_id, "123456").request(params)

    with pytest.raises(UnprocessableEntity):
        WithdrawServices(wallet_id, "123456").request(params)

    with pytest.raises(UnprocessableEntity):
        WithdrawServices(wallet_id, "123456").request(params)
