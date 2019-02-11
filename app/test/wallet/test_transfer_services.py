"""
    Test Transfer Services
"""
from unittest.mock import patch, Mock
from app.api import db

from app.test.base  import BaseTestCase

from app.api.models import Payment
from app.api.models import Wallet
from app.api.models import Transaction
from app.api.models import MasterTransaction
from app.api.models import Bank
from app.api.models import BankAccount

from app.api.common.helper import QR

from app.api.wallet.modules.transfer_services import TransferServices

# exceptions
from app.api.exception.wallet import *

from app.api.exception.bank import BankAccountNotFoundError

class TestTransferServices(BaseTestCase):
    """ Test Class for Transfer Services"""

    def _create_source_destination(self):
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

        return source_wallet, destination_wallet

    def test_create_payment_success(self):
        """ test create payment record"""
        params = {
            "source_account" : "123456",
            "to"             : "123457",
            "amount"         : 12,
            "payment_type"   : True,
        }
        result = TransferServices.create_payment(params)
        self.assertTrue(result > 0)

    def test_internal_transfer_success(self):
        """ test function to create main transaction """
        source, destination = self._create_source_destination()

        params = {
            "amount" : 1,
            "notes" : "Some transfer notes"
        }

        result = TransferServices(source.id, "123456",
                                  destination.id).internal_transfer(params)

        master_trx = MasterTransaction.query.all()
        self.assertTrue(len(master_trx) > 0)
        transaction = Transaction.query.all()
        self.assertTrue(len(transaction) > 0)
        payment = Payment.query.all()
        self.assertTrue(len(payment) > 0)

    def test_internal_transfer_failed_source_not_found(self):
        """ test function to create main transaction """
        # create sourc wallet first
        source, destination = self._create_source_destination()

        params = {
            "source_account" : "12345",
            "to" : destination.id,
            "amount" : 1,
            "pin" : "123456",
        }

        with self.assertRaises(WalletNotFoundError):
            result = TransferServices("90", "123456",
                                      destination.id).internal_transfer(params)

    def test_internal_transfer_failed_source_locked(self):
        """ test function to create main transaction """
        # create sourc wallet first
        source, destination = self._create_source_destination()

        source.lock()
        db.session.commit()

        params = {
            "amount" : 1,
            "notes" : "some transfer notes"
        }

        with self.assertRaises(WalletLockedError):
            result = TransferServices(source.id, "123456",
                                      destination.id).internal_transfer(params)

    def test_internal_transfer_failed_source_wrong_pin(self):
        """ test function to create main transaction """
        source, destination = self._create_source_destination()

        params = {
            "amount" : 1,
            "notes" : "Some transfer notes"
        }

        with self.assertRaises(IncorrectPinError):
            result = TransferServices(source.id, "111111",
                                      destination.id).internal_transfer(params)

    def test_internal_transfer_failed_source_insufficient_balance(self):
        """ test function to create main transaction """
        # create sourc wallet first
        source, destination = self._create_source_destination()
        source.balance = 0
        db.session.commit()

        params = {
            "amount" : 10,
            "notes" : "some transfer notes"
        }

        with self.assertRaises(InsufficientBalanceError):
            result = TransferServices(source.id, "123456",
                                      destination.id).internal_transfer(params)

    def test_internal_transfer_failed_destination_not_found(self):
        """ test function to create main transaction """
        source, destination = self._create_source_destination()

        params = {
            "amount" : 1,
            "notes" : "some transfer notes"
        }

        with self.assertRaises(WalletNotFoundError):
            result = TransferServices(source.id, "123456", "9090").internal_transfer(params)

    def test_internal_transfer_failed_destination_locked(self):
        """ test function to create main transaction """
        # create sourc wallet first
        source, destination = self._create_source_destination()

        destination.lock()
        db.session.commit()

        params = {
            "amount" : 1,
            "notes" : "some transfer notes"
        }

        with self.assertRaises(WalletLockedError):
            result = TransferServices(source.id, "123456",
                                      destination.id).internal_transfer(params)

    def test_internal_transfer_failed_destination_source_same(self):
        """ test function to create main transaction """
        # create sourc wallet first
        source, destination = self._create_source_destination()

        params = {
            "amount" : 1,
            "notes" : "some transfer notes"
        }

        with self.assertRaises(InvalidDestinationError):
            result = TransferServices(source.id, "123456",
                                      source.id).internal_transfer(params)

    @patch.object(TransferServices, "debit_transaction")
    def test_internal_transfer_failed_debit(self, mock_transfer_services):
        """ test function to create main transaction """
        source, destination = self._create_source_destination()

        params = {
            "amount" : 1,
            "notes"  : None
        }

        mock_transfer_services.side_effect = TransactionError("test")
        with self.assertRaises(TransferError):
            TransferServices(source.id, "123456", destination.id).internal_transfer(params)

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

    '''
    @patch.object(TransferServices, "credit_transaction")
    def test_internal_transfer_failed_credit(self, mock_transfer_services):
        """ test function to create main transaction """
        source, destination = self._create_source_destination()

        params = {
            "amount" : 1,
            "notes"  : None
        }

        mock_transfer_services.side_effect = TransactionError("test")
        with self.assertRaises(TransferError):
            TransferServices(source.id, "123456", destination.id).internal_transfer(params)

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
    '''

    def testdebit_transaction_success(self):
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

        transaction_id = TransferServices.debit_transaction(wallet, debit_payment.id, 111, "TRANSFER_IN")
        self.assertTrue(transaction_id, str)

    def testdebit_transaction_failed(self):
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
            TransferServices.debit_transaction(wallet, 1234, 111, "TRANSFER_IN")

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

        transaction_id = TransferServices.credit_transaction(wallet,
                                                             credit_payment.id,
                                                             trx_amount,
                                                             "TRANSFER_IN")
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
            TransferServices.credit_transaction(wallet, 1234, trx_amount, "TRANSFER_IN")

    def test_external_transfer(self):
        """ test function to create main transaction """
        # create sourc wallet first
        source_wallet = Wallet()
        source_wallet.set_pin("123456")
        db.session.add(source_wallet)
        db.session.commit()

        source_wallet.add_balance(1000)
        db.session.flush()

        # add bank account
        bank = Bank.query.filter_by(code="009").first()
        bank_account = BankAccount(account_no="123456", bank_id=bank.id)
        db.session.add(bank_account)
        db.session.commit()

        params = {
            "amount" : 1,
            "destination" : bank_account.id,
            "notes" : None,
        }

        result = TransferServices(source_wallet.id,
                                  "123456").external_transfer(params)

        master_trx = MasterTransaction.query.all()
        self.assertTrue(len(master_trx) > 0)
        transaction = Transaction.query.all()
        self.assertTrue(len(transaction) > 0)
        payment = Payment.query.all()
        self.assertTrue(len(payment) > 0)

    def test_external_transfer_insufficient(self):
        """ test function to create main transaction """
        # create sourc wallet first
        source_wallet = Wallet()
        source_wallet.set_pin("123456")
        db.session.add(source_wallet)
        db.session.commit()

        source_wallet.add_balance(1000)
        db.session.flush()

        # add bank account
        bank = Bank.query.filter_by(code="009").first()
        bank_account = BankAccount(account_no="123456", bank_id=bank.id)
        db.session.add(bank_account)
        db.session.commit()

        params = {
            "amount" : 10000,
            "destination" : bank_account.id,
            "notes" : None,
        }

        with self.assertRaises(InsufficientBalanceError):
            result = TransferServices(source_wallet.id,
                                      "123456").external_transfer(params)

    def test_external_transfer_bank_account_error(self):
        """ test function to create main transaction """
        # create sourc wallet first
        source_wallet = Wallet()
        source_wallet.set_pin("123456")
        db.session.add(source_wallet)
        db.session.commit()

        source_wallet.add_balance(1000)
        db.session.flush()

        # add bank account
        bank = Bank.query.filter_by(code="009").first()
        bank_account = BankAccount(account_no="123456", bank_id=bank.id)
        db.session.add(bank_account)
        db.session.commit()

        params = {
            "amount" : 1,
            "destination" : "123444",
            "notes" : None,
        }

        with self.assertRaises(BankAccountNotFoundError):
            result = TransferServices(source_wallet.id,
                                      "123456").external_transfer(params)

    @patch.object(TransferServices, "debit_transaction")
    def test_external_transfer_debit_failed(self, mock_transfer_services):
        """ test function to create main transaction """
        # create sourc wallet first
        source_wallet = Wallet()
        source_wallet.set_pin("123456")
        db.session.add(source_wallet)
        db.session.commit()

        source_wallet.add_balance(1000)
        db.session.flush()

        # add bank account
        bank = Bank.query.filter_by(code="009").first()
        bank_account = BankAccount(account_no="123456", bank_id=bank.id)
        db.session.add(bank_account)
        db.session.commit()

        params = {
            "amount" : 1,
            "destination" : bank_account.id,
            "notes" : None,
        }

        mock_transfer_services.side_effect = TransactionError("test")
        with self.assertRaises(TransferError):
            TransferServices(source_wallet.id,
                             "123456").external_transfer(params)

        # make sure maste transaction record everything
        master_trx = MasterTransaction.query.all()
        self.assertTrue(len(master_trx) > 0)
        # make sure transaction is not recorded on user transaction
        trx = Transaction.query.all()
        self.assertTrue(len(trx) == 0)
        # make sure the wallet balance isstill same
        wallet = Wallet.query.get(1)
        self.assertEqual(wallet.balance, 1000)
