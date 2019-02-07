"""
    Test Transfer Services
"""
from unittest.mock import patch, Mock
from app.api import db

from app.test.base          import BaseTestCase
from app.api.models         import Payment
from app.api.models         import Wallet
from app.api.models         import Transaction
from app.api.models         import MasterTransaction
from app.api.wallet.modules.transfer_services import TransferServices

# exceptions
from app.api.exception.wallet import WalletNotFoundError
from app.api.exception.wallet import WalletLockedError
from app.api.exception.wallet import IncorrectPinError
from app.api.exception.wallet import InsufficientBalanceError
from app.api.exception.wallet import InvalidDestinationError
from app.api.exception.wallet import TransactionError
from app.api.exception.wallet import TransferError

class TestTransferServices(BaseTestCase):
    """ Test Class for Transfer Services"""

    def test_create_payment_success(self):
        """ test create payment record"""
        params = {
            "source"      : "123456",
            "destination" : "123457",
            "amount"      : 12,
            "payment_type": True,
        }
        result = TransferServices._create_payment(params)
        self.assertTrue(result > 0)

    def test_internal_transfer_success(self):
        """ test function to create main transaction """
        # create sourc wallet first
        source_wallet = Wallet()
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

        params = {
            "amount" : 1,
        }

        result = TransferServices(source_wallet.id, "123456",
                                  destination_wallet.id).internal_transfer(params)

        master_trx = MasterTransaction.query.all()
        self.assertTrue(len(master_trx) > 0)
        transaction = Transaction.query.all()
        self.assertTrue(len(transaction) > 0)
        payment = Payment.query.all()
        self.assertTrue(len(payment) > 0)

    def test_internal_transfer_failed_source_not_found(self):
        """ test function to create main transaction """
        # create sourc wallet first
        source_wallet = Wallet()
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

        params = {
            "source" : "12345",
            "destination" : destination_wallet.id,
            "amount" : 1,
            "pin" : "123456",
        }

        with self.assertRaises(WalletNotFoundError):
            result = TransferServices("90", "123456",
                                      destination_wallet.id).internal_transfer(params)

    def test_internal_transfer_failed_source_locked(self):
        """ test function to create main transaction """
        # create sourc wallet first
        source_wallet = Wallet()
        source_wallet.set_pin("123456")
        db.session.add(source_wallet)
        db.session.commit()

        source_wallet.add_balance(1000)
        source_wallet.lock()
        db.session.commit()

        # create destination wallet secondly
        destination_wallet = Wallet()
        destination_wallet.set_pin("123456")
        db.session.add(destination_wallet)
        db.session.commit()

        params = {
            "amount" : 1,
        }

        with self.assertRaises(WalletLockedError):
            result = TransferServices(source_wallet.id, "123456",
                                     destination_wallet.id).internal_transfer(params)

    def test_internal_transfer_failed_source_wrong_pin(self):
        """ test function to create main transaction """
        # create sourc wallet first
        source_wallet = Wallet()
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

        params = {
            "amount" : 1,
        }

        with self.assertRaises(IncorrectPinError):
            result = TransferServices(source_wallet.id, "111111",
                                      destination_wallet.id).internal_transfer(params)

    def test_internal_transfer_failed_source_insufficient_balance(self):
        """ test function to create main transaction """
        # create sourc wallet first
        source_wallet = Wallet()
        source_wallet.set_pin("123456")
        db.session.add(source_wallet)
        db.session.commit()

        source_wallet.add_balance(1)
        db.session.flush()

        # create destination wallet secondly
        destination_wallet = Wallet()
        destination_wallet.set_pin("123456")
        db.session.add(destination_wallet)
        db.session.commit()

        params = {
            "amount" : 10,
        }

        with self.assertRaises(InsufficientBalanceError):
            result = TransferServices(source_wallet.id, "123456",
                                      destination_wallet.id).internal_transfer(params)

    def test_internal_transfer_failed_destination_not_found(self):
        """ test function to create main transaction """
        # create sourc wallet first
        source_wallet = Wallet()
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

        params = {
            "amount" : 1,
        }

        with self.assertRaises(WalletNotFoundError):
            result = TransferServices(source_wallet.id, "123456", "9090").internal_transfer(params)

    def test_internal_transfer_failed_destination_locked(self):
        """ test function to create main transaction """
        # create sourc wallet first
        source_wallet = Wallet()
        source_wallet.set_pin("123456")
        db.session.add(source_wallet)
        db.session.commit()

        source_wallet.add_balance(1000)
        db.session.flush()

        # create destination wallet secondly
        destination_wallet = Wallet()
        destination_wallet.set_pin("123456")
        db.session.add(destination_wallet)
        db.session.flush()
        destination_wallet.lock()
        db.session.commit()

        params = {
            "amount" : 1,
        }

        with self.assertRaises(WalletLockedError):
            result = TransferServices(source_wallet.id, "123456",
                                      destination_wallet.id).internal_transfer(params)

    def test_internal_transfer_failed_destination_source_same(self):
        """ test function to create main transaction """
        # create sourc wallet first
        source_wallet = Wallet()
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

        params = {
            "amount" : 1,
        }

        with self.assertRaises(InvalidDestinationError):
            result = TransferServices(source_wallet.id, "123456",
                                      source_wallet.id).internal_transfer(params)

    @patch.object(TransferServices, "_debit_transaction")
    def test_internal_transfer_failed_debit(self, mock_transfer_services):
        """ test function to create main transaction """
        # create sourc wallet first
        source_wallet = Wallet()
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

        params = {
            "amount" : 1,
        }

        mock_transfer_services.side_effect = TransactionError("test")
        with self.assertRaises(TransferError):
            TransferServices(source_wallet.id, "123456", destination_wallet.id).internal_transfer(params)

        # make sure maste transaction record everything
        master_trx = MasterTransaction.query.all()
        self.assertTrue(len(master_trx) > 0)
        # make sure transaction is not recorded on user transaction
        trx = Transaction.query.all()
        self.assertTrue(len(trx) == 0)
        # make sure the wallet balance isstill same
        wallet = Wallet.query.get(1)
        self.assertEqual(wallet.balance, 1000)

        wallet2 = Wallet.query.get(2)
        self.assertEqual(wallet2.balance, 0)

    @patch.object(TransferServices, "_credit_transaction")
    def test_internal_transfer_failed_credit(self, mock_transfer_services):
        """ test function to create main transaction """
        # create sourc wallet first
        source_wallet = Wallet()
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

        params = {
            "amount" : 1,
        }

        mock_transfer_services.side_effect = TransactionError("test")
        with self.assertRaises(TransferError):
            TransferServices(source_wallet.id, "123456", destination_wallet.id).internal_transfer(params)

        # make sure maste transaction record everything
        master_trx = MasterTransaction.query.all()
        print(master_trx)
        self.assertTrue(len(master_trx) > 0)
        # make sure transaction is not recorded on user transaction
        trx = Transaction.query.all()
        print(trx)
        self.assertTrue(len(trx) == 0)
        # make sure the wallet balance isstill same
        wallet = Wallet.query.get(1)
        self.assertEqual(wallet.balance, 1000)

        wallet2 = Wallet.query.get(2)
        self.assertEqual(wallet2.balance, 0)

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

        transaction_id = TransferServices._debit_transaction(wallet, debit_payment.id, 111, "IN")
        self.assertTrue(transaction_id, str)

    def test_debit_transaction_failed(self):
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

        with self.assertRaises(TransactionError):
            TransferServices._debit_transaction(wallet, 1234, 111, "IN")

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

        transaction_id = TransferServices._credit_transaction(wallet, credit_payment.id, trx_amount)
        self.assertTrue(transaction_id, str)

    def test_credit_transaction_failed(self):
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

        with self.assertRaises(TransactionError):
            TransferServices._credit_transaction(wallet, 1234, trx_amount)
