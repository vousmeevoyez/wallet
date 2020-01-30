"""
    Test Transaction Factory
"""
from app.api.models import Transaction
from app.api import db

from app.api.transactions.factories.helper import process_transaction


def test_process_transation(setup_wallet_with_balance, setup_wallet_without_balance):
    # this will trigger creation of transaction that move money from a to b
    process_transaction(
        source=setup_wallet_with_balance,
        destination=setup_wallet_without_balance,
        amount=-1000,
        flag="TRANSFER",
        notes="some notes",
    )

    source_trx = Transaction.query.filter_by(
        wallet_id=setup_wallet_with_balance.id
    ).all()
    assert len(source_trx) == 1
