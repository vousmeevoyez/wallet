"""
    Test Transfer Services
"""
import uuid
from datetime import datetime, timedelta
from unittest.mock import patch, Mock
from app.api import db

from app.test.base  import BaseTestCase

from app.api.models import *

from app.api.wallets.modules.transaction_core import TransactionCore
from app.api.wallets.modules.transaction_core import TransactionError
# exceptions
from app.api.error.http import *

fake_wallet_id = str(uuid.uuid4())

class TestTransactionCore(BaseTestCase):
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

    def _create_deposit(self):
        wallet = self.source

        bank = Bank(
              key="BNI",
              code="009"
        )
        db.session.add(bank)
        db.session.commit()

        va_type = VaType.query.filter_by(key="CREDIT").first()

        va = VirtualAccount(wallet_id=wallet.id, va_type_id=va_type.id, bank_id=bank.id)

        va_id = va.generate_va_number()
        trx_id = va.generate_trx_id()
        db.session.add(va)
        db.session.commit()

        params = {
            "payment_amount"      : 10000,
            "payment_ntb"         : "123456",
            "payment_channel_key" : "BNI_VA",
            "virtual_account"     : va.account_no,
        }
        return params

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
                                                             "RECEIVE_PAYROLL")
        self.assertTrue(transaction_id, str)

    def test_create_payment_success(self):
        """ test create payment record"""
        params = {
            "source_account" : "123456",
            "to"             : "123457",
            "amount"         : 12,
            "payment_type"   : True,
            "ref_number"     : "123456",
        }
        result = TransactionCore.create_payment(params)
        self.assertTrue(result)

    def test_create_payment_failed(self):
        """ test create payment failed duplicate ref nmber"""
        params = {
            "source_account" : "123456",
            "to"             : "123457",
            "amount"         : 12,
            "payment_type"   : True,
            "ref_number"     : "123456",
        }
        result = TransactionCore.create_payment(params)
        self.assertTrue(result)

        params = {
            "source_account" : "123456",
            "to"             : "123457",
            "amount"         : 12,
            "payment_type"   : True,
            "ref_number"     : "123456",
        }
        result = TransactionCore.create_payment(params)
        self.assertEqual(result, None)

    def test_process_transaction_debit(self):
        """ test function to process transaction """
        # create sourc wallet first
        params = {
            "amount" : 1,
            "notes" : "some transfer notes",
        }

        result = TransactionCore().process_transaction(
            self.source, self.destination, params['amount'], True,
            "TRANSFER_IN", params['notes']
        )
        self.assertTrue(isinstance(result, object))

    def test_process_transaction_credit(self):
        """ test function to process transaction """
        # create sourc wallet first
        params = {
            "amount" : 1,
            "notes" : "some transfer notes",
        }

        result = TransactionCore().process_transaction(
            self.source, self.destination, params['amount'], False,
            "RECEIVE_TRANSFER", params['notes']
        )
        self.assertTrue(isinstance(result, object))

    def test_process_transaction_bank_account(self):
        """ test function to process transaction from walelt to bank account"""
        # create sourc wallet first
        params = {
            "amount" : 1,
            "notes" : "some transfer notes",
        }

        result = TransactionCore().process_transaction(
            self.source, "12345678", params['amount'], False,
            "TRANSFER_OUT", params['notes']
        )
        self.assertTrue(isinstance(result, object))

    def test_process_transaction_from_bank(self):
        """ test function to process transaction from bank VA """
        payload = self._create_deposit()

        payment_channel = PaymentChannel.query.filter_by(
            key=payload['payment_channel_key']
        ).first()

        result = TransactionCore().process_transaction(
            source=payload['virtual_account'],
            destination=self.source,
            amount=payload['payment_amount'],
            payment_type=True, # CREDIT
            transfer_types="TOP_UP",
            channel_id=payment_channel.id,
            reference_number=payload['payment_ntb']
        )
        self.assertTrue(isinstance(result, object))
        self.assertEqual(len(Payment.query.all()), 1)
        self.assertEqual(len(Transaction.query.all()), 1)

    @patch.object(TransactionCore, "debit_transaction")
    def test_process_transaction_debit_failed(self, mock_transaction_core):
        """ test function to process transaction """
        # create sourc wallet first
        params = {
            "amount" : 1,
            "notes" : "some transfer notes",
        }
        mock_transaction_core.side_effect = TransactionError("some error")

        with self.assertRaises(UnprocessableEntity):
            result = TransactionCore().process_transaction(
                self.source, self.destination, -params['amount'], False,
                "TRANSFER_IN", params['notes']
            )

        # make sure transaction is not recorded on user transaction
        trx = Transaction.query.all()
        self.assertTrue(len(trx) == 0)
        # make sure the wallet balance isstill same
        self.assertEqual(self.source.balance, 10000)
        self.assertEqual(self.destination.balance, 0)

    @patch.object(TransactionCore, "credit_transaction")
    def test_process_transaction_credit_failed(self, mock_transaction_core):
        """ test function to process transaction """
        # create sourc wallet first
        params = {
            "amount" : 1,
            "notes" : "some transfer notes",
        }
        mock_transaction_core.side_effect = TransactionError("some error")

        with self.assertRaises(UnprocessableEntity):
            result = TransactionCore().process_transaction(
                self.source, self.destination, params['amount'], True,
                "RECEIVE_TRANSFER", params['notes']
            )

        # make sure transaction is not recorded on user transaction
        trx = Transaction.query.all()
        self.assertTrue(len(trx) == 0)
        # make sure the wallet balance isstill same
        self.assertEqual(self.source.balance, 10000)
        self.assertEqual(self.destination.balance, 0)
