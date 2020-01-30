import pytest
import time
from unittest.mock import patch

from celery.exceptions import Retry, MaxRetriesExceededError

from app.api import db
from app.api.models import VirtualAccount, Payment, Transaction, Bank

from task.bank.tasks import BankTask
from task.bank.lib.provider import ProviderError

""" Test Class for Bank Worker """


@patch("task.bank.tasks.generate_provider")
def test_create_va(mock_provider, setup_user_wallet_va):
    """ test function that create va in the background """
    # create virtual account credit
    access_token, user_id, wallet_id = setup_user_wallet_va
    va = VirtualAccount.query.filter_by(wallet_id=wallet_id).first()

    plain_data = {"trx_id": va.trx_id, "virtual_account": va.account_no}
    mock_provider.return_value.create_va.return_value = plain_data

    BankTask().create_va(va.id)
    # need to make sure vitual account is activated
    assert va.status == 1


@patch("task.bank.tasks.generate_provider")
def test_update_va(mock_provider, setup_user_wallet_va):
    """ test function that create va in the background """
    # create virtual account credit
    access_token, user_id, wallet_id = setup_user_wallet_va
    va = VirtualAccount.query.filter_by(wallet_id=wallet_id).first()

    # update va name here
    va.name = "cool name"
    db.session.commit()

    plain_data = {"trx_id": va.trx_id, "virtual_account": va.account_no}
    mock_provider.return_value.update_va.return_value = plain_data

    BankTask().update_va(va.id)
    # need to make sure vitual account is activated
    assert va.name == "cool name"


@patch("task.bank.tasks.generate_provider")
def test_bank_transfer_to_bni(
    mock_provider, setup_wallet_with_balance, setup_bni_bank_account
):
    """ test function that transfer money using OPG in the background """
    amount = -100

    payment_payload = {
        "payment_type": False,
        "source_account": setup_wallet_with_balance.id,
        "to": setup_bni_bank_account.account_no,
        "amount": amount,
    }

    payment = Payment(**payment_payload)
    db.session.add(payment)

    debit_transaction = Transaction(
        payment_id=payment.id, wallet_id=setup_wallet_with_balance.id, amount=amount
    )

    db.session.add(debit_transaction)
    db.session.commit()

    expected_value = {
        "transfer_info": {
            "source_account": "113183203",
            "destination_account": "115471119",
            "amount": 100500,
            "bank_ref": "953403",
            "ref_number": "20170227000000000020",
        }
    }

    mock_provider.return_value.transfer.return_value = expected_value

    BankTask().bank_transfer(payment.id)
    assert payment.ref_number


@patch("task.bank.tasks.generate_provider")
@patch("task.bank.tasks.BankTask.retry")
def test_bank_transfer_retry(
    mock_provider, mock_celery, setup_wallet_with_balance, setup_bni_bank_account
):
    """ test function that transfer money using OPG in the background but
    failed and reach max retries """
    amount = -100

    payment_payload = {
        "payment_type": False,
        "source_account": setup_wallet_with_balance.id,
        "to": setup_bni_bank_account.account_no,
        "amount": amount,
    }

    payment = Payment(**payment_payload)
    db.session.add(payment)

    debit_transaction = Transaction(
        payment_id=payment.id, wallet_id=setup_wallet_with_balance.id, amount=amount
    )

    db.session.add(debit_transaction)
    db.session.commit()

    mock_provider.transfer.side_effect = ProviderError("dsdsds")
    mock_celery.side_effect = Retry()

    with pytest.raises(Retry):
        BankTask().bank_transfer(payment.id)


@patch("task.bank.tasks.generate_provider")
@patch("task.bank.tasks.BankTask.retry")
def test_bank_transfer_max_retry(
    mock_core_bank, mock_celery, setup_wallet_with_balance, setup_bni_bank_account
):
    """ test function that transfer money using OPG in the background but
    failed and reach max retries """
    amount = -100

    payment_payload = {
        "payment_type": False,
        "source_account": setup_wallet_with_balance.id,
        "to": setup_bni_bank_account.account_no,
        "amount": amount,
    }

    payment = Payment(**payment_payload)
    db.session.add(payment)

    debit_transaction = Transaction(
        payment_id=payment.id, wallet_id=setup_wallet_with_balance.id, amount=amount
    )

    db.session.add(debit_transaction)
    db.session.commit()

    mock_core_bank.transfer.side_effect = ProviderError("dsdsds")
    mock_celery.side_effect = MaxRetriesExceededError()

    with pytest.raises(MaxRetriesExceededError):
        BankTask().bank_transfer(payment.id)
