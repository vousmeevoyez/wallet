"""
    Test Transfer Services
"""
from unittest.mock import patch, Mock
from app.api import db

from app.test.base          import BaseTestCase
from app.api.models         import Payment
from app.api.models         import Wallet
from app.api.models         import Transaction
from app.api.wallet.modules.transfer_services import TransferServices

# exceptions
from app.api.exception.wallet.exceptions import WalletNotFoundError
from app.api.exception.wallet.exceptions import WalletLockedError
from app.api.exception.wallet.exceptions import IncorrectPinError
from app.api.exception.wallet.exceptions import InsufficientBalanceError
from app.api.exception.wallet.exceptions import InvalidDestinationError
from app.api.exception.wallet.exceptions import TransactionError
from app.api.exception.wallet.exceptions import TransferError

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
        result = TransferServices()._create_payment(params)
        self.assertTrue(result > 0)

    @patch.object(TransferServices, "_do_transaction")
    def test_internal_transfer(self, mock_transfer_services):
        """ test internal transfer between wallet"""
        params = {
            "source" : "1234",
            "destination" : "2234",
            "amount" : "1",
            "pin" : "123456",
        }
        mock_transfer_services.return_value = {
            "status" : "SUCCESS",
            "data"   : "Some Transfer data",
        }

        result = TransferServices().internal_transfer(params)
        self.assertTrue(result["data"])

    @patch.object(TransferServices, "_do_transaction")
    def test_internal_transfer_client_error(self, mock_transfer_services):
        """ test internal transfer between wallet but there's client error"""
        params = {
            "source" : "1234",
            "destination" : "2234",
            "amount" : "1",
            "pin" : "123456",
        }

        mock_transfer_services.side_effect = WalletNotFoundError("123456")
        result = TransferServices().internal_transfer(params)
        self.assertTrue(result[1], 400)

    @patch.object(TransferServices, "_do_transaction")
    def test_internal_transfer_server_error(self, mock_transfer_services):
        """ test internal transfer between wallet but there's server error"""
        params = {
            "source" : "1234",
            "destination" : "2234",
            "amount" : "1",
            "pin" : "123456",
        }

        mock_transfer_services.side_effect = TransferError("Some Error")

        result = TransferServices().internal_transfer(params)
        self.assertTrue(result[1], 500)

    def test_do_transaction_success(self):
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
            "source" : source_wallet.id,
            "destination" : destination_wallet.id,
            "amount" : 1,
            "pin" : "123456",
        }

        result = TransferServices()._do_transaction(params)
        
        transaction = Transaction.query.all()
        self.assertTrue(len(transaction) > 0)
        payment = Payment.query.all()
        self.assertTrue(len(payment) > 0)

    def test_do_transaction_failed_source_not_found(self):
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
            result = TransferServices()._do_transaction(params)

    def test_do_transaction_failed_source_locked(self):
        """ test function to create main transaction """
        # create sourc wallet first
        source_wallet = Wallet()
        source_wallet.set_pin("123456")
        db.session.add(source_wallet)
        db.session.commit()

        source_wallet.add_balance(1000)
        source_wallet.lock()
        db.session.flush()

        # create destination wallet secondly
        destination_wallet = Wallet()
        destination_wallet.set_pin("123456")
        db.session.add(destination_wallet)
        db.session.commit()

        params = {
            "source" : source_wallet.id,
            "destination" : destination_wallet.id,
            "amount" : 1,
            "pin" : "123456",
        }

        with self.assertRaises(WalletLockedError):
            result = TransferServices()._do_transaction(params)

    def test_do_transaction_failed_source_wrong_pin(self):
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
            "source" : source_wallet.id,
            "destination" : destination_wallet.id,
            "amount" : 1,
            "pin" : "103456",
        }


        with self.assertRaises(IncorrectPinError):
            result = TransferServices()._do_transaction(params)

    def test_do_transaction_failed_source_insufficient_balance(self):
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
            "source" : source_wallet.id,
            "destination" : destination_wallet.id,
            "amount" : 10,
            "pin" : "123456",
        }

        with self.assertRaises(InsufficientBalanceError):
            result = TransferServices()._do_transaction(params)

    def test_do_transaction_failed_destination_not_found(self):
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
            "source" : source_wallet.id,
            "destination" : "123456",
            "amount" : 1,
            "pin" : "123456",
        }

        with self.assertRaises(WalletNotFoundError):
            result = TransferServices()._do_transaction(params)

    def test_do_transaction_failed_destination_locked(self):
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
            "source" : source_wallet.id,
            "destination" : destination_wallet.id,
            "amount" : 1,
            "pin" : "123456",
        }

        with self.assertRaises(WalletLockedError):
            result = TransferServices()._do_transaction(params)

    def test_do_transaction_failed_destination_source_same(self):
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
            "source" : source_wallet.id,
            "destination" : source_wallet.id,
            "amount" : 1,
            "pin" : "123456",
        }

        with self.assertRaises(InvalidDestinationError):
            result = TransferServices()._do_transaction(params)

    @patch.object(TransferServices, "_debit_transaction")
    def test_do_transaction_failed_debit(self, mock_transfer_services):
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
            "source" : source_wallet.id,
            "destination" : destination_wallet.id,
            "amount" : 1,
            "pin" : "123456",
        }

        mock_transfer_services.side_effect = TransactionError("test")
        with self.assertRaises(TransferError):
            TransferServices()._do_transaction(params)

    @patch.object(TransferServices, "_credit_transaction")
    def test_do_transaction_failed_credit(self, mock_transfer_services):
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
            "source" : source_wallet.id,
            "destination" : destination_wallet.id,
            "amount" : 1,
            "pin" : "123456",
        }

        mock_transfer_services.side_effect = TransactionError("test")
        with self.assertRaises(TransferError):
            TransferServices()._do_transaction(params)

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

        TransferServices()._debit_transaction(wallet, debit_payment.id, 111, "IN")

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
            TransferServices()._debit_transaction(wallet, 1234, 111, "IN")

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

        TransferServices()._credit_transaction(wallet, credit_payment.id, trx_amount)

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
            TransferServices()._credit_transaction(wallet, 1234, trx_amount)
