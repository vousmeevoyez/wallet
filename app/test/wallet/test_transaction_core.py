"""
    Test Transfer Services
"""
import uuid
from unittest.mock import patch, Mock
from app.api import db

from app.test.base  import BaseTestCase

from app.api.models import Payment
from app.api.models import Wallet
from app.api.models import Transaction
from app.api.models import Bank
from app.api.models import BankAccount
from app.api.models import Log

from app.api.utility.utils import QR

from app.api.wallet.modules.transaction_core import TransactionCore

# exceptions
from app.api.error.http import *

from task.bank.tasks import BankTask

fake_wallet_id = str(uuid.uuid4())

class TestTransactionCore(BaseTestCase):
    """ Test Class for Transfer Services"""
    def test_debit_transaction_success(self):
        wallet = Wallet()
        db.session.add(wallet)
        db.session.flush()
        wallet.add_balance(1000)

        wallet2 = Wallet()
        db.session.add(wallet2)
        db.session.flush()

        #start transaction here
        trx_amount = 10
        # first create debit payment
        debit_payment = Payment(
            source_account=wallet.id,
            to=wallet2.id,
            amount=trx_amount,
            payment_type=False,
        )
        db.session.add(debit_payment)
        db.session.flush()

        transaction_id = TransactionCore.debit_transaction(wallet, debit_payment.id, 111, "TRANSFER_IN")
        self.assertTrue(transaction_id, str)

    def test_credit_transaction_success(self):
        wallet = Wallet()
        db.session.add(wallet)
        db.session.flush()

        wallet2 = Wallet()
        db.session.add(wallet2)
        db.session.flush()

        #start transaction here
        trx_amount = 10
        # first create debit payment
        credit_payment = Payment(
            source_account=wallet.id,
            to=wallet2.id,
            amount=trx_amount,
            payment_type=True,
        )
        db.session.add(credit_payment)
        db.session.flush()

        transaction_id = TransactionCore.credit_transaction(wallet,
                                                             credit_payment.id,
                                                             trx_amount,
                                                             "TRANSFER_IN")
        self.assertTrue(transaction_id, str)
