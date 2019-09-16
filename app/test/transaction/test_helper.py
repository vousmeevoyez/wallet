"""
    Test Transaction Factory
"""
from app.test.base import BaseTestCase

from app.api.models import *
from app.api import db

from app.api.transactions.factories.helper import process_transaction


class TestHelper(BaseTestCase):
    def test_process_transation(self):
        wallet = Wallet()
        wallet2 = Wallet()

        db.session.add(wallet)
        db.session.add(wallet2)
        db.session.commit()

        result = process_transaction(
            source=wallet,
            destination=wallet2,
            amount=1000,
            flag="TRANSFER",
            notes="some notes",
        )
        print(result)
