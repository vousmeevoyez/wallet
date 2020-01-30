"""
    Integration Testing between va & routes
"""
from unittest.mock import Mock, patch

from app.api.models import VirtualAccount, VaLog
from app.api import db

from tests.reusable.api_list import (
    get_virtual_account,
    get_virtual_accounts,
    get_virtual_account_logs,
    update_virtual_account,
)


"""
    TEST VIRTUAL ACCOUNTS
"""


def test_get_virtual_accounts(client, setup_user_wallet_va, setup_admin_token):
    result = get_virtual_accounts(client, setup_admin_token)
    response = result.get_json()
    assert len(response["data"]) > 0


def test_update_virtual_account(client, setup_user_wallet_va, setup_admin_token):
    access_token, user_id, wallet_id = setup_user_wallet_va

    va = VirtualAccount.query.filter_by(wallet_id=wallet_id).first()
    account_no = va.account_no

    data = {"name": "my updated name", "datetime_expired": "2019-11-22"}

    result = update_virtual_account(client, setup_admin_token, account_no, data)
    assert result.status_code == 204
    # make sure its updated!
    assert va.name == data["name"]

    data = {"name": "my updated name2"}

    result = update_virtual_account(client, setup_admin_token, account_no, data)
    assert result.status_code == 204
    # make sure its updated!
    assert va.name == data["name"]


def test_get_virtual_account(client, setup_user_wallet_va, setup_admin_token):
    result = get_virtual_accounts(client, setup_admin_token)
    response = result.get_json()
    va_account_no = response["data"][0]["account_no"]

    result = get_virtual_account(client, va_account_no, setup_admin_token)
    response = result.get_json()
    assert response["data"]
    assert response["data"]["account_no"]
    assert response["data"]["va_type"]
    assert response["data"]["name"]
    assert response["data"]["status"]
    assert response["data"]["bank_name"]
    assert response["data"]["trx_id"]


def test_get_virtual_account_logs(client, setup_user_wallet_va, setup_admin_token):
    result = get_virtual_accounts(client, setup_admin_token)
    response = result.get_json()
    va_account_no = response["data"][0]["account_no"]

    result = get_virtual_account_logs(client, va_account_no, setup_admin_token)
    response = result.get_json()
    assert response["data"] == []
