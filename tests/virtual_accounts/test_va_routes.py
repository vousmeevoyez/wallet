"""
    Integration Testing between va & routes
"""
from unittest.mock import Mock, patch

from app.api.models import VirtualAccount, VaLog
from app.api import db

from tests.reusable.api_list import (
    get_virtual_account,
    get_virtual_accounts,
    get_virtual_account_logs
)


"""
    TEST VIRTUAL ACCOUNTS
"""

def test_get_virtual_accounts(client, setup_user_wallet_va, setup_admin_token):
    result = get_virtual_accounts(client, setup_admin_token)
    response = result.get_json()
    assert len(response["data"]) > 0


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
