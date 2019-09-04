"""
    Test Transfer Services
"""
import uuid

from unittest.mock import patch

from app.api import db

from app.test.base  import BaseTestCase

from app.api.models import *

from app.api.utility.utils import QR

from app.api.transfer.modules.transfer_services import TransferServices
from app.api.transactions.factories import helper as transaction_helper
from app.api.transactions.factories.transactions.products import TransactionError

# callback for unittest purpose
from app.api.callback.modules.callback_services import CallbackServices

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
            "payment_amount" : 10000,
            "payment_ntb" : "123456",
            "payment_channel_key" : "BNI_VA"
        }
        result = CallbackServices(va.account_no, trx_id).deposit(params)
        self.assertEqual(result['status'], '000')

        transaction = Transaction.query.join(
            TransactionType, Transaction.transaction_type_id ==
            TransactionType.id
        ).filter(
            Transaction.wallet_id == wallet.id,
            TransactionType.key == "TOP_UP",
        ).first()
        return transaction.id

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

    '''
    def test_internal_transfer_with_auto_pay(self):
        """ test function to create main transaction """
        # create payment plan
        payment_plan = PaymentPlan(
            destination="12345678910",
            wallet_id=self.destination.id
        )
        db.session.add(payment_plan)
        db.session.commit()

        # create plan
        due_date = datetime.utcnow()
        january_plan = Plan(
            payment_plan_id=payment_plan.id,
            amount=10,
            due_date=due_date
        )
        db.session.add(january_plan)
        db.session.commit()

        # register destination as bank account
        bni = Bank(
            key="BNI",
            code="009"
        )
        db.session.add(bni)
        db.session.commit()

        bank_account = BankAccount(
            account_no="12345678910",
            bank_id=bni.id
        )
        db.session.add(bank_account)
        db.session.commit()

        params = {
            "amount" : 10000,
            "types"  : "PAYROLL",
            "notes" : "Some transfer notes",
        }

        result = TransferServices(str(self.source.id), "123456",
                                  str(self.destination.id)).internal_transfer(params)

        time.sleep(3)
        transaction = Transaction.query.all()
        print(transaction)
    '''

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

    @patch.object(BankTask, "bank_transfer")
    def test_external_transfer(self, mock_bank_transfer):
        """ test function to create main transaction """
        params = {
            "amount" : 1,
            "destination" : str(self.bank_account.id),
            "notes" : None,
        }

        mock_bank_transfer.return_value = True

        result = TransferServices(
            str(self.source.id), "123456"
        ).external_transfer(params)

        transaction = Transaction.query.all()
        self.assertTrue(len(transaction) > 0)
        payment = Payment.query.all()
        self.assertTrue(len(payment) > 0)

    def test_external_transfer_insufficient(self):
        """ test function to create main transaction """
        params = {
            "amount" : 100000,
            "destination" : str(self.bank_account.id),
            "notes" : None,
        }

        with self.assertRaises(UnprocessableEntity):
            result = TransferServices(
                str(self.source.id), "123456"
            ).external_transfer(params)

    def test_external_transfer_bank_account_error(self):
        """ test function to create main transaction """
        # add bank account
        params = {
            "amount" : 1,
            "destination" : fake_wallet_id,
            "notes" : None,
        }

        with self.assertRaises(RequestNotFound):
            result = TransferServices(
                str(self.source.id), "123456"
            ).external_transfer(params)

    '''
    @patch(transaction_helper, "process_transaction")
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
            result = TransferServices(
                str(self.source.id), "123456"
            ).external_transfer(params)

        # make sure transaction is not recorded on user transaction
        trx = Transaction.query.all()
        self.assertTrue(len(trx) == 0)
        # make sure the wallet balance isstill same
        self.assertEqual(self.source.balance, 10000)
    '''

    def test_calculate_transfer_fee(self):
        #  Wallet to Wallet Transfer
        result = \
        TransferServices().calculate_transfer_fee(str(self.destination.id))
        # should be zero
        self.assertEqual(result, 0)

        # wallet to BNI transfer
        result = \
        TransferServices().calculate_transfer_fee(str(self.bank_account.id),
                                                "ONLINE")
        # should be zero
        self.assertEqual(result, 0)

        # wallet to BCA transfer Online
        result = \
        TransferServices().calculate_transfer_fee(str(self.bank_account2.id),
                                                "ONLINE")
        # should be 6500
        self.assertEqual(result, 6500)

        # wallet to BCA transfer Clearing
        result = \
        TransferServices().calculate_transfer_fee(str(self.bank_account2.id),
                                                "CLEARING")
        # should be 5000
        self.assertEqual(result, 5000)

    def test_checkout(self):
        """ test checkout function """
        result = TransferServices().checkout("62", "88308644314")[0]
        self.assertTrue(result["data"])
