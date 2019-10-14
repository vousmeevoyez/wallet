"""
    Test Transfer Services
"""
import pytest
import uuid

from unittest.mock import patch

from app.api import db

from app.api.models import Transaction, Payment, Wallet

from app.api.utility.utils import QR

from app.api.transfer.modules.transfer_services import TransferServices
from app.api.transactions.factories import helper as transaction_helper
from app.api.transactions.factories.transactions.products import TransactionError

# callback for unittest purpose
from app.api.callback.modules.callback_services import CallbackServices

# exceptions
from app.api.error.http import *

from task.bank.tasks import BankTask

fake_wallet_id = str(uuid.uuid4())


def test_internal_transfer_success(setup_user_wallet_va,
                                   setup_user_wallet_va_without_balance):
    """ test function to create main transaction """

    source_access_token, source_user_id, source_wallet_id = \
        setup_user_wallet_va
    destination_access_token, destination_user_id, destination_wallet_id = \
        setup_user_wallet_va_without_balance

    params = {"amount": 1, "notes": "Some transfer notes", "types": None}

    result = TransferServices(
        source_wallet_id, "123456", destination_wallet_id
    ).internal_transfer(params)

    transaction = Transaction.query.all()
    assert len(transaction) > 0
    payment = Payment.query.all()
    assert len(payment) > 0


def test_internal_transfer_failed_invalid_id(setup_user_wallet_va,
                                             setup_user_wallet_va_without_balance):
    """ test function to create main transaction """
    # create sourc wallet first
    source_access_token, source_user_id, source_wallet_id = \
        setup_user_wallet_va
    destination_access_token, destination_user_id, destination_wallet_id = \
        setup_user_wallet_va_without_balance

    params = {"amount": 1, "notes": "Some transfer notes", "types": None}

    with pytest.raises(BadRequest):
        result = TransferServices(
            "90", "123456", destination_wallet_id
        ).internal_transfer(params)

def test_internal_transfer_failed_source_not_found(setup_user_wallet_va,
                                                   setup_user_wallet_va_without_balance):
    """ test function to create main transaction """
    # create sourc wallet first
    source_access_token, source_user_id, source_wallet_id = \
        setup_user_wallet_va
    destination_access_token, destination_user_id, destination_wallet_id = \
        setup_user_wallet_va_without_balance

    params = {"amount": 1, "notes": "Some transfer notes", "types": None}

    with pytest.raises(RequestNotFound):
        result = TransferServices(
            fake_wallet_id, "123456",
            destination_wallet_id
        ).internal_transfer(params)

def test_internal_transfer_failed_source_locked(setup_user_wallet_va,
                                                setup_user_wallet_va_without_balance):
    """ test function to create main transaction """
    source_access_token, source_user_id, source_wallet_id = \
        setup_user_wallet_va
    destination_access_token, destination_user_id, destination_wallet_id = \
        setup_user_wallet_va_without_balance

    # create sourc wallet first
    wallet = Wallet.query.get(source_wallet_id)
    wallet.lock()
    db.session.commit()

    params = {"amount": 1, "notes": "some transfer notes", "types": None}

    with pytest.raises(UnprocessableEntity):
        result = TransferServices(
            source_wallet_id, "123456", destination_wallet_id
        ).internal_transfer(params)

    wallet.unlock()
    db.session.commit()

def test_internal_transfer_failed_source_wrong_pin(setup_user_wallet_va,
                                                   setup_user_wallet_va_without_balance):
    """ test function to create main transaction """
    source_access_token, source_user_id, source_wallet_id = \
        setup_user_wallet_va
    destination_access_token, destination_user_id, destination_wallet_id = \
        setup_user_wallet_va_without_balance

    params = {"amount": 1, "notes": "Some transfer notes", "types": None}

    with pytest.raises(UnprocessableEntity):
        result = TransferServices(
            source_wallet_id,
            "111111",
            destination_wallet_id
        ).internal_transfer(params)

def test_internal_transfer_failed_source_max_wrong_pin(setup_user_wallet_va,
                                                       setup_user_wallet_va_without_balance):
    """ test function to create main transaction """
    source_access_token, source_user_id, source_wallet_id = \
        setup_user_wallet_va
    destination_access_token, destination_user_id, destination_wallet_id = \
        setup_user_wallet_va_without_balance

    params = {"amount": 1, "notes": "Some transfer notes", "types": None}

    with pytest.raises(UnprocessableEntity):
        result = TransferServices(
            source_wallet_id, "111111", destination_wallet_id
        ).internal_transfer(params)

    with pytest.raises(UnprocessableEntity):
        result = TransferServices(
            source_wallet_id, "111111", destination_wallet_id
        ).internal_transfer(params)

    with pytest.raises(UnprocessableEntity):
        result = TransferServices(
            source_wallet_id, "111111", destination_wallet_id
        ).internal_transfer(params)

    with pytest.raises(UnprocessableEntity):
        result = TransferServices(
            source_wallet_id, "111111", destination_wallet_id
        ).internal_transfer(params)

    wallet = Wallet.query.get(source_wallet_id)
    wallet.unlock()
    db.session.commit()


def test_internal_transfer_failed_insufficient(setup_user_wallet_va,
                                               setup_user_wallet_va_without_balance):
    """ test function to create main transaction """
    # create sourc wallet first
    source_access_token, source_user_id, source_wallet_id = \
        setup_user_wallet_va
    destination_access_token, destination_user_id, destination_wallet_id = \
        setup_user_wallet_va_without_balance

    params = {"amount": 10, "notes": "some transfer notes", "types": None}

    with pytest.raises(UnprocessableEntity):
        result = TransferServices(
            destination_wallet_id, "123456", source_wallet_id
        ).internal_transfer(params)

def test_internal_transfer_failed_destination_not_found(setup_user_wallet_va,
                                                        setup_user_wallet_va_without_balance):
    """ test function to create main transaction """
    source_access_token, source_user_id, source_wallet_id = \
        setup_user_wallet_va
    destination_access_token, destination_user_id, destination_wallet_id = \
        setup_user_wallet_va_without_balance

    params = {"amount": 1, "notes": "some transfer notes", "types": None}

    with pytest.raises(RequestNotFound):
        result = TransferServices(
            source_wallet_id, "123456", fake_wallet_id
        ).internal_transfer(params)

def test_internal_transfer_failed_destination_locked(setup_user_wallet_va,
                                                     setup_user_wallet_va_without_balance):
    """ test function to create main transaction """
    # create sourc wallet first
    source_access_token, source_user_id, source_wallet_id = \
        setup_user_wallet_va
    destination_access_token, destination_user_id, destination_wallet_id = \
        setup_user_wallet_va_without_balance

    wallet = Wallet.query.get(destination_wallet_id)
    wallet.lock()
    db.session.commit()

    params = {"amount": 1, "notes": "some transfer notes", "types": None}

    with pytest.raises(UnprocessableEntity):
        result = TransferServices(
            source_wallet_id, "123456", destination_wallet_id
        ).internal_transfer(params)

    wallet = Wallet.query.get(destination_wallet_id)
    wallet.unlock()
    db.session.commit()

def test_internal_transfer_failed_destination_source_same(setup_user_wallet_va,
                                                          setup_user_wallet_va_without_balance):
    """ test function to create main transaction """
    # create sourc wallet first
    source_access_token, source_user_id, source_wallet_id = \
        setup_user_wallet_va
    destination_access_token, destination_user_id, destination_wallet_id = \
        setup_user_wallet_va_without_balance

    params = {"amount": 1, "notes": "some transfer notes", "types": None}

    with pytest.raises(UnprocessableEntity):
        result = TransferServices(
            source_wallet_id, "123456", source_wallet_id
        ).internal_transfer(params)

@patch.object(BankTask, "bank_transfer")
def test_external_transfer(mock_bank_transfer, setup_user_wallet_va_bank_acc):
    """ test function to create main transaction """
    source_access_token, source_user_id, source_wallet_id, source_bank_acc_id = \
        setup_user_wallet_va_bank_acc

    params = {"amount": 1, "destination": source_bank_acc_id, "notes": None}

    mock_bank_transfer.return_value = True

    result = TransferServices(source_wallet_id, "123456").external_transfer(
        params
    )

    transaction = Transaction.query.all()
    assert len(transaction) > 0
    payment = Payment.query.all()
    assert len(payment) > 0

def test_external_transfer_insufficient(setup_user_wallet_va_bank_acc):
    """ test function to create main transaction """
    source_access_token, source_user_id, source_wallet_id, source_bank_acc_id = \
        setup_user_wallet_va_bank_acc

    params = {
        "amount": 99999999,
        "destination": source_bank_acc_id,
        "notes": None,
    }

    with pytest.raises(UnprocessableEntity):
        result = TransferServices(source_wallet_id, "123456").external_transfer(
            params
        )

def test_external_transfer_bank_account_error(setup_user_wallet_va_bank_acc):
    """ test function to create main transaction """
    # add bank account
    source_access_token, source_user_id, source_wallet_id, source_bank_acc_id = \
        setup_user_wallet_va_bank_acc

    params = {"amount": 1, "destination": fake_wallet_id, "notes": None}

    with pytest.raises(RequestNotFound):
        result = TransferServices(source_wallet_id, "123456").external_transfer(
            params
        )


def test_calculate_transfer_fee(setup_bca_bank_account,
                                setup_bni_bank_account):

    #  Wallet to Wallet Transfer
    result = TransferServices.calculate_transfer_fee(fake_wallet_id)
    # should be zero
    assert result == 0

    # wallet to BNI transfer
    result = TransferServices.calculate_transfer_fee(
        str(setup_bni_bank_account.id), "ONLINE"
    )
    # should be zero
    assert result == 0

    # wallet to BCA transfer Online
    result = TransferServices.calculate_transfer_fee(
        str(setup_bca_bank_account.id), "ONLINE"
    )
    # should be 6500
    assert result == 6500

    # wallet to BCA transfer Clearing
    result = TransferServices.calculate_transfer_fee(
        str(setup_bca_bank_account.id), "CLEARING"
    )
    # should be 5000
    assert result == 5000


def test_checkout(setup_user_only, setup_wallet_without_balance):
    """ test checkout function """
    setup_wallet_without_balance.user = setup_user_only
    db.session.commit()

    result = TransferServices().checkout("62", "88308644314")[0]
    assert result["data"]
