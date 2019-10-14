import time

from app.api import db
from app.api.models import Payment, Transaction, Wallet

from app.api.transactions.factories.helper import process_transaction
from task.transaction.tasks import TransactionTask


def test_transfer(setup_wallet_with_balance, setup_wallet_without_balance):
    """
        DEBIT TRANSFER
    """
    amount = 100
    original_source_balance = setup_wallet_with_balance.balance

    transaction = process_transaction(
        source=setup_wallet_with_balance,
        destination=setup_wallet_without_balance,
        amount=-amount,
        flag="TRANSFER",
        notes="test transfer"
    )
    # exchange transaction id for payment id
    payment = Payment.query.filter_by(transaction=transaction).first()
    # send for apply !
    TransactionTask().transfer(payment.id)
    # make sure payment is completed
    assert payment.status == 1

    # make sure wallet deducted
    source = Wallet.query.get(setup_wallet_with_balance.id)
    assert source.balance == original_source_balance - amount

    """
        CREDIT TRANSFER
    """

    original_destination_balance = setup_wallet_without_balance.balance

    transaction = process_transaction(
        source=setup_wallet_with_balance,
        destination=setup_wallet_without_balance,
        amount=amount,
        flag="RECEIVE_TRANSFER",
        notes="test transfer"
    )

    # exchange transaction id for payment id
    payment = Payment.query.filter_by(transaction=transaction).first()
    # send for apply !
    TransactionTask().transfer(payment.id)
    # make sure payment is completed
    assert payment.status == 1

    # make sure wallet deducted
    destination = Wallet.query.get(setup_wallet_without_balance.id)
    assert destination.balance == original_destination_balance + amount
