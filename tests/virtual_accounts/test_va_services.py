"""
    Test Wallet Services
"""
from unittest.mock import patch, Mock
from app.api import db

from app.api.models import *

from task.bank.tasks import BankTask

from app.api.virtual_accounts.modules.va_services import VirtualAccountServices
from app.api.const import STATUS


@patch.object(BankTask, "create_va")
def test_add_va(mock_create_va, setup_wallet_info):
    """ test method for creating va"""
    virtual_account = VirtualAccount(name="lisa")

    params = {
        "bank_code": "009",
        "type": "CREDIT",
        "wallet_id": setup_wallet_info["id"],
        "amount": 0
    }

    mock_create_va.return_value = True
    result = VirtualAccountServices().add(virtual_account, params)
    assert result[0]["data"]["virtual_account"]


@patch.object(BankTask, "create_va")
def test_info_va(mock_create_va, setup_wallet_info):
    """ test method for returning va information """
    virtual_account = VirtualAccount(name="lisa")

    params = {
        "bank_code": "009",
        "type": "CREDIT",
        "wallet_id": setup_wallet_info["id"],
        "amount": 0
    }

    mock_create_va.return_value = True
    result = VirtualAccountServices().add(virtual_account, params)
    virtual_account = result[0]["data"]["virtual_account"]

    result = VirtualAccountServices(virtual_account).info()
    assert result["data"]


@patch.object(BankTask, "create_va")
def test_update_va(mock_create_va, setup_wallet_info):
    """ test method for updating va information """
    virtual_account = VirtualAccount(name="lisa")

    params = {
        "bank_code": "009",
        "type": "CREDIT",
        "wallet_id": setup_wallet_info["id"],
        "amount": 0
    }

    mock_create_va.return_value = True
    result = VirtualAccountServices().add(virtual_account, params)
    virtual_account = result[0]["data"]["virtual_account"]

    params = {
        "name": "more cool name update",
        "datetime_expired": "2029-11-22"
    }
    result = VirtualAccountServices(virtual_account).update(params)
    # make sure its updated
    va = VirtualAccount.query.filter_by(account_no=virtual_account).first()
    assert va.name == "more cool name update"


@patch.object(BankTask, "create_va")
def test_show(mock_create_va, setup_wallet_info):
    """ test method for showing all va"""
    virtual_account = VirtualAccount(name="lisa")

    params = {
        "bank_code": "009",
        "type": "CREDIT",
        "wallet_id": setup_wallet_info["id"],
        "amount": 0
    }

    mock_create_va.return_value = True
    result = VirtualAccountServices().add(virtual_account, params)
    assert result[0]["data"]["virtual_account"]

    result = VirtualAccountServices().show()
    assert len(result) >= 2


def test_get_logs(setup_bank, setup_credit_va_type):
    """ test method for showing all va logs """
    # create dummy logs for testing!
    va = VirtualAccount(name="lisa", bank_id=setup_bank.id,
                        va_type_id=setup_credit_va_type.id)
    va.generate_trx_id()
    va.generate_va_number()
    db.session.add(va)
    db.session.commit()

    va_log = VaLog(
        virtual_account_id=va.id, balance=1000
    )

    va_log2 = VaLog(
        virtual_account_id=va.id, balance=1100
    )

    va_log3 = VaLog(
        virtual_account_id=va.id, balance=1200
    )

    db.session.add(va_log)
    db.session.add(va_log2)
    db.session.add(va_log3)
    db.session.commit()

    result = VirtualAccountServices(
        virtual_account_no=va.account_no
    ).get_logs()
    data = result[0]["data"]
    # make sure it return a right data
    assert len(data) >= 3
    # have 2 balance and created at
    assert data[0]["balance"]
    assert data[0]["created_at"]
