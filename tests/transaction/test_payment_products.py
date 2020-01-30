"""
    Test Payment Products
"""
from app.api.models import Payment

from app.api.transactions.factories.payments.products import CreditPayment, DebitPayment


def test_credit_payment():
    payment = Payment(source_account="123456", to="123455", amount=1000)

    credit_payment = CreditPayment()
    credit_payment.load(payment)

    result = credit_payment.create()
    assert result


def test_debit_payment():
    payment = Payment(source_account="123456", to="123455", amount=-1000)

    debit_payment = DebitPayment()
    debit_payment.load(payment)

    result = debit_payment.create()
    assert result
