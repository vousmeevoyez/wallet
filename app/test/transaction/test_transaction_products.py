"""
    Test Transaction Products
"""
from datetime import datetime, timedelta

from freezegun import freeze_time

from app.test.base  import BaseTestCase

from app.api import db

from app.api.models import (
    Payment,
    Transaction,
    Wallet,
    TransactionType,
    Bank,
    BankAccount,
    Payment,
    PaymentPlan,
    Plan
)

from app.api.transactions.factories.transactions.products import (
    DebitTransaction,
    CreditTransaction,
    ReceivePayrollTransaction
)

class TestTransactionProduct(BaseTestCase):

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

    def test_credit_transaction(self):
        wallet = Wallet()
        wallet2 = Wallet()

        db.session.add(wallet)
        db.session.add(wallet2)
        db.session.commit()

        credit_payment = Payment(
            source_account=str(wallet.id),
            to=str(wallet2.id),
            amount=1000,
            payment_type=True
        )

        transaction = Transaction(
            wallet=wallet,
            amount=1000,
            notes="some transfer",
            payment=credit_payment
        )

        credit_transaction = CreditTransaction()
        credit_transaction.load(transaction)
        result = credit_transaction.create("TOP_UP")
        self.assertTrue(result)

    def test_debit_transaction(self):
        wallet = Wallet()
        wallet2 = Wallet()

        db.session.add(wallet)
        db.session.add(wallet2)
        db.session.commit()

        debit_payment = Payment(
            source_account=str(wallet.id),
            to=str(wallet2.id),
            amount=-1000,
            payment_type=False
        )

        transaction = Transaction(
            wallet=wallet,
            amount=1000,
            notes="some transfer",
            payment=debit_payment,
        )

        debit_transaction = DebitTransaction()
        debit_transaction.load(transaction)
        result = debit_transaction.create("TRANSFER")
        self.assertTrue(result)

    def test_receive_payroll_without_payment_plan(self):
        wallet = Wallet()
        wallet2 = Wallet()

        db.session.add(wallet)
        db.session.add(wallet2)
        db.session.commit()

        debit_payment = Payment(
            source_account=str(wallet.id),
            to=str(wallet2.id),
            amount=-1000,
            payment_type=False
        )

        transaction = Transaction(
            wallet=wallet,
            amount=1000,
            notes="Terima gaji",
            payment=debit_payment,
        )

        receive_payroll_transaction = ReceivePayrollTransaction()
        receive_payroll_transaction.load(transaction)

        result = receive_payroll_transaction.post_create("RECEIVE_PAYROLL")
        self.assertEqual(result, {})

    def test_receive_payroll_less_payroll(self):
        debit_payment = Payment(
            source_account=str(self.source.id),
            to=str(self.destination.id),
            amount=-1000,
            payment_type=False
        )

        transaction = Transaction(
            wallet=self.source,
            amount=1000,
            notes="Terima gaji",
            payment=debit_payment,
        )

        # create payment plan
        payment_plan = PaymentPlan(
            destination="12345678910",
            wallet_id=self.source.id
        )
        db.session.add(payment_plan)
        db.session.commit()

        # create plan
        due_date = datetime.utcnow().replace(hour=0, minute=1, second=0)
        january_plan = Plan(
            payment_plan_id=payment_plan.id,
            amount=100000,
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

        receive_payroll_transaction = ReceivePayrollTransaction()
        receive_payroll_transaction.load(transaction)

        result = receive_payroll_transaction.post_create("RECEIVE_PAYROLL")
        self.assertEqual(result["data"]["message"], "AUTO_DEBIT")

    def test_receive_payroll_early_payroll(self):
        debit_payment = Payment(
            source_account=str(self.source.id),
            to=str(self.destination.id),
            amount=-1000,
            payment_type=False
        )

        transaction = Transaction(
            wallet=self.source,
            amount=1000,
            notes="Terima gaji",
            payment=debit_payment,
        )

        # create payment plan
        payment_plan = PaymentPlan(
            destination="12345678910",
            wallet_id=self.source.id
        )
        db.session.add(payment_plan)
        db.session.commit()

        # create plan
        due_date = datetime.utcnow() + timedelta(days=1)

        january_plan = Plan(
            payment_plan_id=payment_plan.id,
            amount=100000,
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

        receive_payroll_transaction = ReceivePayrollTransaction()
        receive_payroll_transaction.load(transaction)

        result = receive_payroll_transaction.post_create("RECEIVE_PAYROLL")
        self.assertEqual(result["data"]["message"], "AUTO_DEBIT")

    @freeze_time("2019-04-29")
    def test_receive_payroll_late_payroll(self):
        debit_payment = Payment(
            source_account=str(self.source.id),
            to=str(self.destination.id),
            amount=-1000,
            payment_type=False
        )

        transaction = Transaction(
            wallet=self.source,
            amount=1000,
            notes="Terima gaji",
            payment=debit_payment,
        )

        # create payment plan
        payment_plan = PaymentPlan(
            destination="12345678910",
            wallet_id=self.source.id
        )
        db.session.add(payment_plan)
        db.session.commit()

        # create plan
        due_date = datetime.utcnow() - timedelta(days=1)

        january_plan = Plan(
            payment_plan_id=payment_plan.id,
            amount=100000,
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

        receive_payroll_transaction = ReceivePayrollTransaction()
        receive_payroll_transaction.load(transaction)

        result = receive_payroll_transaction.post_create("RECEIVE_PAYROLL")
        self.assertEqual(result, {})

