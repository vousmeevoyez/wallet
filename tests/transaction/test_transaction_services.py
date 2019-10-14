"""
    Test Transfer Services
"""
import pytest
import uuid
from unittest.mock import patch, Mock
from app.api import db

from app.api.models import Transaction, Payment

from app.api.transactions.modules.transaction_services import TransactionServices

# unittest purpose
from app.api.callback.modules.callback_services import CallbackServices
from app.api.transfer.modules.transfer_services import TransferServices

# exceptions
from app.api.error.http import *

from task.bank.tasks import BankTask

fake_wallet_id = str(uuid.uuid4())


def test_refund_transfer(setup_wallet_with_balance,
                         setup_wallet_without_balance):
    """ test function to create transaction refund on transfer between user """
    params = {"amount": 1, "notes": "Some transfer notes", "types": None}

    result = TransferServices(
        str(setup_wallet_with_balance.id),
        "123456",
        str(setup_wallet_without_balance.id)
    ).internal_transfer(params)

    transaction = Transaction.query.all()
    assert len(transaction) > 0

    payment = Payment.query.all()
    assert len(payment) > 0

    # transaction_id
    transaction_id = result[0]["data"]["id"]

    # refund a transfer here
    result = TransactionServices(transaction_id=transaction_id).refund()
    # should generate 2 refunded transaction
    assert len(result[0]["data"]) == 2


def test_refund_ext_transfer_without_fee(setup_wallet_with_balance,
                                         setup_bni_bank_account):
    """ test function to refund an external transfer without transaction
    fee """
    params = {"amount": 1, "destination": str(setup_bni_bank_account.id), "notes": None}

    result = TransferServices(
        str(setup_wallet_with_balance.id),
        "123456"
    ).external_transfer(
        params
    )

    transaction = Transaction.query.all()
    assert len(transaction) > 0
    payment = Payment.query.all()
    assert len(payment) > 0

    # transaction_id
    transaction_id = result[0]["data"]["id"]

    # refund a transfer here
    result = TransactionServices(transaction_id=transaction_id).refund()
    assert len(result[0]["data"]) == 1  # because not trf fee


def test_refund_ext_transfer_with_fee(setup_wallet_with_balance,
                                      setup_bca_bank_account):
    """ test function to refund an external transfer with transaction
    fee """

    params = {"amount": 1, "destination": str(setup_bca_bank_account.id), "notes": None}

    result = TransferServices(
        str(setup_wallet_with_balance.id),
        "123456"
    ).external_transfer(
        params
    )

    transaction = Transaction.query.all()
    assert len(transaction) > 0
    payment = Payment.query.all()
    assert len(payment) > 0

    # transaction_id
    transaction_id = result[0]["data"]["id"]

    # refund a transfer here
    result = TransactionServices(transaction_id=transaction_id).refund()
    assert len(result[0]["data"]) == 2  # because with trf fee


def test_refund_transfer_failed(setup_wallet_with_balance,
                                setup_wallet_without_balance):
    """ test function to create transaction refund with transaction that
    already refunded """
    params = {"amount": 1, "notes": "Some transfer notes", "types": None}

    result = TransferServices(
        str(setup_wallet_with_balance.id),
        "123456",
        str(setup_wallet_without_balance.id)
    ).internal_transfer(params)

    transaction = Transaction.query.all()
    assert len(transaction) > 0
    payment = Payment.query.all()
    assert len(payment) > 0

    # transaction_id
    transaction_id = result[0]["data"]["id"]

    # refund a transfer here
    result = TransactionServices(transaction_id=transaction_id).refund()
    # should generate 2 refunded transaction
    assert len(result[0]["data"]) == 2

    with pytest.raises(UnprocessableEntity):
        # should raise an error because transaction already refunded
        result = TransactionServices(transaction_id=transaction_id).refund()


def test_refund_transfer_failed_invalid(setup_wallet_with_balance,
                                        setup_wallet_without_balance):
    """ test function to create transaction refund on refund transaction
    """
    params = {"amount": 1, "notes": "Some transfer notes", "types": None}

    result = TransferServices(
        str(setup_wallet_with_balance.id),
        "123456",
        str(setup_wallet_without_balance.id)
    ).internal_transfer(params)

    transaction = Transaction.query.all()
    assert len(transaction) > 0
    payment = Payment.query.all()
    assert len(payment) > 0

    # transaction_id
    transaction_id = result[0]["data"]["id"]

    # refund a transfer here
    result = TransactionServices(transaction_id=transaction_id).refund()
    # should generate 2 refunded transaction
    assert len(result[0]["data"]) == 2

    refunded_transaction_id = result[0]["data"][0]["id"]

    with pytest.raises(UnprocessableEntity):
        # should raise an error because transaction already refunded
        result = TransactionServices(
            transaction_id=refunded_transaction_id
        ).refund()


def test_wallet_in_history(setup_wallet_with_balance):
    """ test method for checking wallet in transaction on wallet history """
    params = {"start_date": "2019/02/01", "end_date": "2019/02/02", "flag": "IN"}
    result = TransactionServices(
        str(setup_wallet_with_balance.id)
    ).history(params)[0]["data"]

    assert result == []


def test_wallet_out_history(setup_wallet_with_balance):
    """ test method for checking wallet out transaction on wallet history """
    result = TransactionServices(
        str(setup_wallet_with_balance.id)
    ).history(
        {"start_date": "2019/02/01", "end_date": "2019/02/02", "flag": "OUT"}
    )[0]["data"]

    assert result == []
