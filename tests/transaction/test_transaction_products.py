"""
    Test Transaction Products
"""
from datetime import datetime, timedelta

from freezegun import freeze_time

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
    Plan,
)

from app.api.transactions.factories.transactions.products import (
    DebitTransaction,
    CreditTransaction,
    ReceivePayrollTransaction,
)


def test_credit_transaction(setup_wallet_with_balance, setup_wallet_without_balance):
    credit_payment = Payment(
        source_account=str(setup_wallet_with_balance.id),
        to=str(setup_wallet_without_balance.id),
        amount=1000,
        payment_type=True,
    )

    transaction = Transaction(
        wallet=setup_wallet_with_balance,
        amount=1000,
        notes="some transfer",
        payment=credit_payment,
    )

    credit_transaction = CreditTransaction()
    credit_transaction.load(transaction)
    result = credit_transaction.create("TOP_UP")
    assert result


def test_debit_transaction(setup_wallet_with_balance, setup_wallet_without_balance):
    debit_payment = Payment(
        source_account=str(setup_wallet_with_balance.id),
        to=str(setup_wallet_without_balance.id),
        amount=-1000,
        payment_type=False,
    )

    transaction = Transaction(
        wallet=setup_wallet_with_balance,
        amount=-1000,
        notes="some transfer",
        payment=debit_payment,
    )

    debit_transaction = DebitTransaction()
    debit_transaction.load(transaction)
    result = debit_transaction.create("TRANSFER")
    assert result


def test_receive_payroll_without_payment_plan(
    setup_wallet_with_balance, setup_wallet_without_balance
):
    debit_payment = Payment(
        source_account=str(setup_wallet_with_balance.id),
        to=str(setup_wallet_without_balance.id),
        amount=-1000,
        payment_type=False,
    )

    transaction = Transaction(
        wallet=setup_wallet_with_balance,
        amount=1000,
        notes="Terima gaji",
        payment=debit_payment,
    )

    receive_payroll_transaction = ReceivePayrollTransaction()
    receive_payroll_transaction.load(transaction)

    result = receive_payroll_transaction.post_create("RECEIVE_PAYROLL")
    assert len(result) == 0


def test_receive_payroll_less_payroll(
    setup_wallet_with_balance, setup_wallet_without_balance
):
    debit_payment = Payment(
        source_account=str(setup_wallet_with_balance),
        to=str(setup_wallet_without_balance),
        amount=-1000,
        payment_type=False,
    )

    transaction = Transaction(
        wallet=setup_wallet_with_balance,
        amount=1000,
        notes="Terima gaji",
        payment=debit_payment,
    )

    # create payment plan
    payment_plan = PaymentPlan(
        destination="12345678910", wallet=setup_wallet_with_balance
    )
    db.session.add(payment_plan)
    db.session.commit()

    # create plan
    due_date = datetime.utcnow().replace(hour=0, minute=1, second=0)
    january_plan = Plan(
        payment_plan_id=payment_plan.id, amount=100000, due_date=due_date
    )
    db.session.add(january_plan)
    db.session.commit()

    # register destination as bank account
    bni = Bank(key="BNI", code="009")
    db.session.add(bni)
    db.session.commit()

    bank_account = BankAccount(account_no="12345678910", bank_id=bni.id)
    db.session.add(bank_account)
    db.session.commit()

    receive_payroll_transaction = ReceivePayrollTransaction()
    receive_payroll_transaction.load(transaction)

    result = receive_payroll_transaction.post_create("RECEIVE_PAYROLL")
    assert any("AUTO_DEBIT" in payment_plan["message"] for payment_plan in result)


def test_receive_payroll_early_payroll(
    setup_wallet_with_balance, setup_wallet_without_balance
):
    debit_payment = Payment(
        source_account=str(setup_wallet_with_balance.id),
        to=str(setup_wallet_without_balance.id),
        amount=-1000,
        payment_type=False,
    )

    transaction = Transaction(
        wallet=setup_wallet_with_balance,
        amount=1000,
        notes="Terima gaji",
        payment=debit_payment,
    )

    # create payment plan
    payment_plan = PaymentPlan(
        destination="12345678910", wallet=setup_wallet_with_balance
    )
    db.session.add(payment_plan)
    db.session.commit()

    # create plan
    due_date = datetime.utcnow() + timedelta(days=1)

    january_plan = Plan(
        payment_plan_id=payment_plan.id, amount=100000, due_date=due_date
    )
    db.session.add(january_plan)
    db.session.commit()

    # register destination as bank account
    bni = Bank(key="BNI", code="009")
    db.session.add(bni)
    db.session.commit()

    bank_account = BankAccount(account_no="12345678910", bank_id=bni.id)
    db.session.add(bank_account)
    db.session.commit()

    receive_payroll_transaction = ReceivePayrollTransaction()
    receive_payroll_transaction.load(transaction)

    result = receive_payroll_transaction.post_create("RECEIVE_PAYROLL")
    assert any("AUTO_DEBIT" in payment_plan["message"] for payment_plan in result)


@freeze_time("2019-04-29")
def test_receive_payroll_late_payroll(
    setup_wallet_with_balance, setup_wallet_without_balance
):
    debit_payment = Payment(
        source_account=str(setup_wallet_with_balance.id),
        to=str(setup_wallet_without_balance.id),
        amount=-1000,
        payment_type=False,
    )

    transaction = Transaction(
        wallet=setup_wallet_with_balance,
        amount=1000,
        notes="Terima gaji",
        payment=debit_payment,
    )

    # create payment plan
    payment_plan = PaymentPlan(
        destination="12345678910", wallet=setup_wallet_with_balance
    )
    db.session.add(payment_plan)
    db.session.commit()

    # create plan
    due_date = datetime.utcnow() - timedelta(days=1)

    january_plan = Plan(
        payment_plan_id=payment_plan.id, amount=100000, due_date=due_date
    )
    db.session.add(january_plan)
    db.session.commit()

    # register destination as bank account
    bni = Bank(key="BNI", code="009")
    db.session.add(bni)
    db.session.commit()

    bank_account = BankAccount(account_no="12345678910", bank_id=bni.id)
    db.session.add(bank_account)
    db.session.commit()

    receive_payroll_transaction = ReceivePayrollTransaction()
    receive_payroll_transaction.load(transaction)

    result = receive_payroll_transaction.post_create("RECEIVE_PAYROLL")
    assert any("AUTO_DEBIT" in payment_plan["message"] for payment_plan in result)
