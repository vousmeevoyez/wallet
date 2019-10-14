"""
    Test User Bank Account SErvices
"""
import pytest
import uuid

from app.api.users.modules.bank_account_services import BankAccountServices

from app.api.models import BankAccount

from app.config import config

from app.api.error.http import *

fake_uuid = str(uuid.uuid4())


def test_add_bank_account_success(setup_user_factory):
    """ test add bank account """
    user = setup_user_factory("someuser")

    params = {"label": "sample label", "name": "jennie", "account_no": "1234567891"}
    bank_account = BankAccount(**params)

    result = BankAccountServices(str(user.id), "009").add(bank_account)
    assert result[1] == 201

def test_add_bank_account_failed_user_not_found(setup_user_factory):
    """ test add bank account but not found"""
    params = {"label": "sample label", "name": "jennie", "account_no": "1234567891"}
    bank_account = BankAccount(**params)

    with pytest.raises(RequestNotFound):
        result = BankAccountServices(fake_uuid, "009").add(bank_account)

def test_add_bank_account_failed_bank_not_found(setup_user_factory):
    """ test add bank account but bank not found"""
    user = setup_user_factory("some-user")

    params = {"label": "sample label", "name": "jennie", "account_no": "1234567891"}
    bank_account = BankAccount(**params)

    with pytest.raises(RequestNotFound):
        result = BankAccountServices(str(user.id), fake_uuid).add(bank_account)

def test_show_bank_account_success(setup_user_factory):
    """ test function that show all bank account"""
    user = setup_user_factory("someuser")
    result = BankAccountServices(str(user.id)).show()
    assert len(result) == 1

def test_show_bank_account_failed_record_not_found():
    """ test function that show all bank account but user not found"""
    with pytest.raises(RequestNotFound):
        result = BankAccountServices(fake_uuid).show()

def test_update_bank_account_success(setup_user_factory):
    """ test function that update bank account information"""
    user = setup_user_factory("someuser")

    result = BankAccountServices(str(user.id)).show()
    assert len(result) == 1

    user_bank_account_id = result[0]["id"]

    params = {"label": "my label", "name": "jennie", "account_no": "1234567891"}
    result = BankAccountServices(
        str(user.id), "009", user_bank_account_id
    ).update(params)

    assert result[1] == 204

def test_update_bank_account_failed_bank_account_not_found(setup_user_factory):
    """ test function to update bank account information but account not
    found"""
    user = setup_user_factory("someuser")

    params = {"label": "my label", "name": "jennie", "account_no": "1234567891"}
    with pytest.raises(RequestNotFound):
        result = BankAccountServices(str(user.id), "009", fake_uuid).update(
            params
        )

def test_update_bank_account_failed_bank_not_found(setup_user_factory):
    """ test update bank account but bank no tofund"""
    user = setup_user_factory("someuser")

    result = BankAccountServices(str(user.id)).show()
    assert len(result) == 1

    params = {"label": "my label", "name": "jennie", "account_no": "1234567891"}
    with pytest.raises(RequestNotFound):
        result = BankAccountServices(str(user.id), "999", fake_uuid).update(
            params
        )

def test_remove_bank_account_success(setup_user_factory):
    """ tst function to remove bank account """
    user = setup_user_factory("someuser")

    result = BankAccountServices(str(user.id)).show()
    assert len(result) == 1

    user_bank_account_id = result[0]["id"]

    result = BankAccountServices(
        user_id=str(user.id), bank_account_id=user_bank_account_id
    ).remove()
    assert result[1] == 204
