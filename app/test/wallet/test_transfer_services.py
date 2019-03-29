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

from app.api.wallet.modules.transfer_services import TransferServices
from app.api.wallet.modules.transaction_core  import TransactionCore
from app.api.wallet.modules.transfer_services import TransactionError

# exceptions
from app.api.error.http import *

from task.bank.tasks import BankTask

fake_wallet_id = str(uuid.uuid4())

class TestTransferServices(BaseTestCase):
    """ Test Class for Transfer Services"""

    def setUp(self):
        super().setUp()

        source_wallet = Wallet(user_id=self.user.id)
        source_wallet.set_pin("123456")
        db.session.add(source_wallet)
        db.session.commit()

        source_wallet.add_balance(1000)
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

    def test_create_payment_success(self):
        """ test create payment record"""
        params = {
            "source_account" : "123456",
            "to"             : "123457",
            "amount"         : 12,
            "payment_type"   : True,
        }
        result = TransferServices.create_payment(params)

    def test_internal_transfer_success(self):
        """ test function to create main transaction """
        params = {
            "amount" : 1,
            "notes" : "Some transfer notes",
            "types" : None
        }

        result = TransferServices(str(self.source.id), "123456",
                                  str(self.destination.id)).internal_transfer(params)

        transaction = Transaction.query.all()
        self.assertTrue(len(transaction) > 0)
        payment = Payment.query.all()
        self.assertTrue(len(payment) > 0)

    def test_internal_transfer_failed_invalid_id(self):
        """ test function to create main transaction """
        # create sourc wallet first
        params = {
            "amount" : 1,
            "notes" : "Some transfer notes",
            "types" : None
        }

        with self.assertRaises(BadRequest):
            result = TransferServices("90", "123456",
                                      str(self.destination.id)).internal_transfer(params)

    def test_internal_transfer_failed_source_not_found(self):
        """ test function to create main transaction """
        # create sourc wallet first
        params = {
            "amount" : 1,
            "notes" : "Some transfer notes",
            "types" : None
        }

        with self.assertRaises(RequestNotFound):
            result = TransferServices(fake_wallet_id, "123456",
                                      str(self.destination.id)).internal_transfer(params)

    def test_internal_transfer_failed_source_locked(self):
        """ test function to create main transaction """
        # create sourc wallet first
        self.source.lock()
        db.session.commit()

        params = {
            "amount" : 1,
            "notes" : "some transfer notes",
            "types" : None
        }

        with self.assertRaises(UnprocessableEntity):
            result = TransferServices(str(self.source.id), "123456",
                                      str(self.destination.id)).internal_transfer(params)

    def test_internal_transfer_failed_source_wrong_pin(self):
        """ test function to create main transaction """
        params = {
            "amount" : 1,
            "notes" : "Some transfer notes",
            "types" : None
        }

        with self.assertRaises(UnprocessableEntity):
            result = TransferServices(str(self.source.id), "111111",
                                      str(self.destination.id)).internal_transfer(params)

    def test_internal_transfer_failed_source_max_wrong_pin(self):
        """ test function to create main transaction """
        params = {
            "amount" : 1,
            "notes" : "Some transfer notes",
            "types" : None
        }

        with self.assertRaises(UnprocessableEntity):
            result = TransferServices(str(self.source.id), "111111",
                                      str(self.destination.id)).internal_transfer(params)

        with self.assertRaises(UnprocessableEntity):
            result = TransferServices(str(self.source.id), "111111",
                                      str(self.destination.id)).internal_transfer(params)

        with self.assertRaises(UnprocessableEntity):
            result = TransferServices(str(self.source.id), "111111",
                                      str(self.destination.id)).internal_transfer(params)

        with self.assertRaises(UnprocessableEntity):
            result = TransferServices(str(self.source.id), "111111",
                                      str(self.destination.id)).internal_transfer(params)


    def test_internal_transfer_failed_source_insufficient_balance(self):
        """ test function to create main transaction """
        # create sourc wallet first
        self.source.balance = 0
        db.session.commit()

        params = {
            "amount" : 10,
            "notes" : "some transfer notes",
            "types" : None
        }

        with self.assertRaises(UnprocessableEntity):
            result = TransferServices(str(self.source.id), "123456",
                                      str(self.destination.id)).internal_transfer(params)

    def test_internal_transfer_failed_destination_not_found(self):
        """ test function to create main transaction """
        params = {
            "amount" : 1,
            "notes" : "some transfer notes",
            "types" : None
        }

        with self.assertRaises(RequestNotFound):
            result = TransferServices(str(self.source.id), "123456", fake_wallet_id).internal_transfer(params)

    def test_internal_transfer_failed_destination_locked(self):
        """ test function to create main transaction """
        # create sourc wallet first
        self.destination.lock()
        db.session.commit()

        params = {
            "amount" : 1,
            "notes" : "some transfer notes",
            "types" : None
        }

        with self.assertRaises(UnprocessableEntity):
            result = TransferServices(str(self.source.id), "123456",
                                      str(self.destination.id)).internal_transfer(params)

    def test_internal_transfer_failed_destination_source_same(self):
        """ test function to create main transaction """
        # create sourc wallet first
        params = {
            "amount" : 1,
            "notes" : "some transfer notes",
            "types" : None
        }

        with self.assertRaises(UnprocessableEntity):
            result = TransferServices(str(self.source.id), "123456",
                                      str(self.source.id)).internal_transfer(params)

    @patch.object(TransactionCore, "debit_transaction")
    def test_internal_transfer_failed_debit(self, mock_transfer_services):
        """ test function to create main transaction """
        params = {
            "amount" : 1,
            "notes"  : None,
            "types" : None
        }

        mock_transfer_services.side_effect = TransactionError("test")
        with self.assertRaises(UnprocessableEntity):
            TransferServices(str(self.source.id), "123456", str(self.destination.id)).internal_transfer(params)

        # make sure transaction is not recorded on user transaction
        trx = Transaction.query.all()
        self.assertTrue(len(trx) == 0)
        # make sure the wallet balance isstill same
        self.assertEqual(self.source.balance, 1000)
        self.assertEqual(self.destination.balance, 0)

    @patch.object(BankTask, "bank_transfer")
    def test_external_transfer(self, mock_bank_transfer):
        """ test function to create main transaction """
        params = {
            "amount" : 1,
            "destination" : str(self.bank_account.id),
            "notes" : None,
        }

        mock_bank_transfer.return_value = True

        result = TransferServices(str(self.source.id),
                                  "123456").external_transfer(params)

        transaction = Transaction.query.all()
        self.assertTrue(len(transaction) > 0)
        payment = Payment.query.all()
        self.assertTrue(len(payment) > 0)

    def test_external_transfer_insufficient(self):
        """ test function to create main transaction """
        params = {
            "amount" : 10000,
            "destination" : str(self.bank_account.id),
            "notes" : None,
        }

        with self.assertRaises(UnprocessableEntity):
            result = TransferServices(str(self.source.id),
                                      "123456").external_transfer(params)

    def test_external_transfer_bank_account_error(self):
        """ test function to create main transaction """
        # add bank account
        params = {
            "amount" : 1,
            "destination" : fake_wallet_id,
            "notes" : None,
        }

        with self.assertRaises(RequestNotFound):
            result = TransferServices(str(self.source.id),
                                      "123456").external_transfer(params)

    @patch.object(TransactionCore, "debit_transaction")
    def test_external_transfer_debit_failed(self, mock_transfer_services):
        """ test function to create main transaction """
        # add bank account
        params = {
            "amount" : 1,
            "destination" : str(self.bank_account.id),
            "notes" : None,
        }

        mock_transfer_services.side_effect = TransactionError("test")
        with self.assertRaises(UnprocessableEntity):
            TransferServices(str(self.source.id),
                             "123456").external_transfer(params)

        # make sure transaction is not recorded on user transaction
        trx = Transaction.query.all()
        self.assertTrue(len(trx) == 0)
        # make sure the wallet balance isstill same
        self.assertEqual(self.source.balance, 1000)

    def test_calculate_transfer_fee(self):
        #  Wallet to Wallet Transfer
        result = \
        TransferServices.calculate_transfer_fee(str(self.destination.id))
        # should be zero
        self.assertEqual(result, 0)

        # wallet to BNI transfer
        result = \
        TransferServices.calculate_transfer_fee(str(self.bank_account.id),
                                                "ONLINE")
        # should be zero
        self.assertEqual(result, 0)

        # wallet to BCA transfer Online
        result = \
        TransferServices.calculate_transfer_fee(str(self.bank_account2.id),
                                                "ONLINE")
        # should be 6500
        self.assertEqual(result, 6500)

        # wallet to BCA transfer Clearing
        result = \
        TransferServices.calculate_transfer_fee(str(self.bank_account2.id),
                                                "CLEARING")
        # should be 5000
        self.assertEqual(result, 5000)

    def test_checkout(self):
        """ test checkout function """
        result = TransferServices.checkout("62", "89289644314")[0]
        self.assertTrue(result["data"])
