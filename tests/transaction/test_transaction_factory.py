"""
    Test Transaction Factory
"""
from app.api.models import (
    Transaction,
    Payment
)
from app.api import db

from app.api.transactions.factories.transactions.factory import generate_transaction


def test_generate_transaction(setup_wallet_with_balance,
                              setup_wallet_without_balance):

    credit_payment = Payment(
        source_account=str(setup_wallet_with_balance.id),
        to=str(setup_wallet_without_balance.id),
        amount=1113,
        payment_type=True,
    )

    transaction = Transaction(
        wallet=setup_wallet_with_balance, amount=1113, notes="some transfer", payment=credit_payment
    )

    result = generate_transaction(transaction, "TRANSFER")
    assert result

    # make sure transaction and payment created
    payment = Payment.query.filter_by(amount=1113).first()
    assert payment

    trx = Transaction.query.filter_by(
        wallet_id=setup_wallet_with_balance.id,
        amount=1113
    ).first()
    assert trx
