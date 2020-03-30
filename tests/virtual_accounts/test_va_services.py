"""
    Test Wallet Services
"""
from datetime import datetime
from unittest.mock import patch
from app.api import db

from app.api.models import *

from task.bank.tasks import BankTask

from app.api.banks.modules.bank_services import BankServices
from app.api.virtual_accounts.modules.va_services import VirtualAccountServices
from app.api.virtual_accounts.modules.va_services import bulk_update_va
from app.api.const import STATUS


@patch.object(BankTask, "create_va")
def test_add_va(mock_create_va, setup_wallet_info):
    """ test method for creating va"""
    params = {
        "name": "lisa",
        "bank_code": "009",
        "va_type": "CREDIT",
        "wallet_id": setup_wallet_info["id"],
        "amount": 0,
    }

    mock_create_va.return_value = True
    result = VirtualAccountServices.add(**params)
    assert result[0]["data"]["virtual_account"]


def test_info_va(setup_credit_va):
    """ test method for returning va information """
    va = setup_credit_va[2]
    result = VirtualAccountServices(va.account_no).info()
    assert result["data"]


def test_update_va(setup_credit_va):
    """ test method for updating va information """
    va = setup_credit_va[2]
    params = {"name": "more cool name update", "datetime_expired": "2029-11-22"}
    result = VirtualAccountServices(va.account_no).update(**params)
    assert result[1] == 204

    # make sure its updated
    va = setup_credit_va[2]
    va = VirtualAccount.query.filter_by(account_no=va.account_no).first()
    assert va.name == "more cool name update"


def test_show():
    """ test method for showing all va"""
    result = VirtualAccountServices().show()
    assert len(result) >= 1


def test_get_logs(setup_credit_va):
    """ test method for showing all va logs """
    # create dummy logs for testing!
    va = setup_credit_va[2]
    va_log = VaLog(virtual_account_id=va.id, balance=1000)
    va_log2 = VaLog(virtual_account_id=va.id, balance=1100)
    va_log3 = VaLog(virtual_account_id=va.id, balance=1200)

    db.session.add(va_log)
    db.session.add(va_log2)
    db.session.add(va_log3)
    db.session.commit()

    result = VirtualAccountServices(virtual_account_no=va.account_no).get_logs()
    data = result[0]["data"]
    # make sure it return a right data
    assert len(data) >= 3
    # have 2 balance and created at
    assert data[0]["balance"]
    assert data[0]["created_at"]


def test_remove_va(setup_credit_va):
    """ test method for deactivating va"""
    va = setup_credit_va[2]
    result = VirtualAccountServices(va.account_no).remove()
    assert result[1] == 204


@patch.object(BankServices, "get_account_information")
def test_bulk_update_va_extend(mock_bank_acc_info, setup_credit_va):
    """ test method for bulk update va but existing va still active so it
    should be extend current va """
    mock_bank_acc_info.return_value = {"bank_account_info": {"status": "1"}}

    va = setup_credit_va[2]
    va.status = STATUS["ACTIVE"]
    db.session.commit()

    bulk_update_va()

    virtual_account = VirtualAccount.query.filter_by(account_no=va.account_no).first()
    # approximately 9 year from now
    future_year = datetime.utcnow().year + 9
    assert virtual_account.datetime_expired.year >= future_year


@patch.object(BankServices, "get_account_information")
def test_bulk_update_va_recreate(mock_bank_acc_info, setup_credit_va):
    """ test method for bulk update va but existing va still active so it
    should be extend current va """
    mock_bank_acc_info.return_value = {"bank_account_info": {"status": "2"}}

    va = setup_credit_va[2]
    va.status = STATUS["ACTIVE"]
    db.session.commit()

    bulk_update_va()

    virtual_account = VirtualAccount.query.filter_by(account_no=va.account_no).first()
    # approximately 9 year from now
    future_year = datetime.utcnow().year + 9
    assert virtual_account.datetime_expired.year >= future_year
