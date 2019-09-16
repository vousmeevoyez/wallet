"""
    Test Transaction Factory
"""
from app.test.base import BaseTestCase

from app.api.models import *
from app.api import db

from app.api.transactions.factories.transactions.factory import generate_transaction


class TestTransactionFactory(BaseTestCase):
    def test_generate_transaction(self):
        wallet = Wallet()
        wallet2 = Wallet()

        db.session.add(wallet)
        db.session.add(wallet2)
        db.session.commit()

        credit_payment = Payment(
            source_account=str(wallet.id),
            to=str(wallet2.id),
            amount=1000,
            payment_type=True,
        )

        transaction = Transaction(
            wallet=wallet, amount=1000, notes="some transfer", payment=credit_payment
        )

        result = generate_transaction(transaction, "TRANSFER")
        self.assertTrue(result)
