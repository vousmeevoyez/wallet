"""
    Test Transfer Services
"""
import uuid
from unittest.mock import patch, Mock
from app.api import db

from app.test.base import BaseTestCase

from app.api.models import *

from app.api.transactions.modules.transaction_services import TransactionServices

# unittest purpose
from app.api.callback.modules.callback_services import CallbackServices
from app.api.transfer.modules.transfer_services import TransferServices

# exceptions
from app.api.error.http import *

from task.bank.tasks import BankTask

fake_wallet_id = str(uuid.uuid4())


class TestTransactionServices(BaseTestCase):
    """ Test Class for Transfer Services"""

    def setUp(self):
        super().setUp()

        source_wallet = Wallet(user_id=self.user.id)
        source_wallet.set_pin("123456")
        db.session.add(source_wallet)
        db.session.commit()

        source_wallet.add_balance(10000)
        db.session.flush()

        # create destination wallet secondly
        destination_wallet = Wallet()
        destination_wallet.set_pin("123456")
        db.session.add(destination_wallet)
        db.session.commit()

        # bank account
        bank = Bank.query.filter_by(code="009").first()
        bank_account = BankAccount(account_no="123456", bank_id=bank.id)
        db.session.add(bank_account)
        db.session.commit()

        # bank account
        bank2 = Bank.query.filter_by(code="014").first()
        bank_account2 = BankAccount(account_no="121456", bank_id=bank2.id)
        db.session.add(bank_account2)
        db.session.commit()

        self.source = source_wallet
        self.destination = destination_wallet
        self.bank_account = bank_account
        self.bank_account2 = bank_account2

    # end def

    def test_refund_transfer(self):
        """ test function to create transaction refund on transfer between user """
        params = {"amount": 1, "notes": "Some transfer notes", "types": None}

        result = TransferServices(
            str(self.source.id), "123456", str(self.destination.id)
        ).internal_transfer(params)

        transaction = Transaction.query.all()
        self.assertTrue(len(transaction) > 0)
        payment = Payment.query.all()
        self.assertTrue(len(payment) > 0)

        # transaction_id
        transaction_id = result[0]["data"]["id"]

        # refund a transfer here
        result = TransactionServices(transaction_id=transaction_id).refund()
        # should generate 2 refunded transaction
        self.assertEqual(len(result[0]["data"]), 2)

    def test_refund_ext_transfer_without_fee(self):
        """ test function to refund an external transfer without transaction
        fee """
        params = {"amount": 1, "destination": str(self.bank_account.id), "notes": None}

        result = TransferServices(str(self.source.id), "123456").external_transfer(
            params
        )

        transaction = Transaction.query.all()
        self.assertTrue(len(transaction) > 0)
        payment = Payment.query.all()
        self.assertTrue(len(payment) > 0)

        # transaction_id
        transaction_id = result[0]["data"]["id"]

        # refund a transfer here
        result = TransactionServices(transaction_id=transaction_id).refund()
        self.assertEqual(len(result[0]["data"]), 1)  # because not trf fee

    def test_refund_ext_transfer_with_fee(self):
        """ test function to refund an external transfer with transaction
        fee """

        params = {"amount": 1, "destination": str(self.bank_account2.id), "notes": None}

        result = TransferServices(str(self.source.id), "123456").external_transfer(
            params
        )

        transaction = Transaction.query.all()
        self.assertTrue(len(transaction) > 0)
        payment = Payment.query.all()
        self.assertTrue(len(payment) > 0)

        # transaction_id
        transaction_id = result[0]["data"]["id"]

        # refund a transfer here
        result = TransactionServices(transaction_id=transaction_id).refund()
        self.assertEqual(len(result[0]["data"]), 2)  # because with trf fee

    def test_refund_transfer_failed(self):
        """ test function to create transaction refund with transaction that
        already refunded """
        params = {"amount": 1, "notes": "Some transfer notes", "types": None}

        result = TransferServices(
            str(self.source.id), "123456", str(self.destination.id)
        ).internal_transfer(params)

        transaction = Transaction.query.all()
        self.assertTrue(len(transaction) > 0)
        payment = Payment.query.all()
        self.assertTrue(len(payment) > 0)

        # transaction_id
        transaction_id = result[0]["data"]["id"]

        # refund a transfer here
        result = TransactionServices(transaction_id=transaction_id).refund()
        # should generate 2 refunded transaction
        self.assertEqual(len(result[0]["data"]), 2)

        with self.assertRaises(UnprocessableEntity):
            # should raise an error because transaction already refunded
            result = TransactionServices(transaction_id=transaction_id).refund()

    def test_refund_transfer_failed_invalid(self):
        """ test function to create transaction refund on refund transaction
        """
        params = {"amount": 1, "notes": "Some transfer notes", "types": None}

        result = TransferServices(
            str(self.source.id), "123456", str(self.destination.id)
        ).internal_transfer(params)

        transaction = Transaction.query.all()
        self.assertTrue(len(transaction) > 0)
        payment = Payment.query.all()
        self.assertTrue(len(payment) > 0)

        # transaction_id
        transaction_id = result[0]["data"]["id"]

        # refund a transfer here
        result = TransactionServices(transaction_id=transaction_id).refund()
        # should generate 2 refunded transaction
        self.assertEqual(len(result[0]["data"]), 2)

        refunded_transaction_id = result[0]["data"][0]["id"]
        with self.assertRaises(UnprocessableEntity):
            # should raise an error because transaction already refunded
            result = TransactionServices(
                transaction_id=refunded_transaction_id
            ).refund()

    def test_wallet_in_history(self):
        """ test method for checking wallet in transaction on wallet history """
        params = {"start_date": "2019/02/01", "end_date": "2019/02/02", "flag": "IN"}
        result = TransactionServices(str(self.source.id)).history(params)[0]["data"]
        self.assertEqual(result, [])

    def test_wallet_out_history(self):
        """ test method for checking wallet out transaction on wallet history """
        result = TransactionServices(str(self.source.id)).history(
            {"start_date": "2019/02/01", "end_date": "2019/02/02", "flag": "OUT"}
        )[0]["data"]
        self.assertEqual(result, [])
