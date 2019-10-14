"""
    Test Payment Products
"""
from app.api.models import Payment

from app.api.transactions.factories.payments.factory import generate_payment


def test_generate_payment():
    payment = Payment(source_account="123456", to="123455", amount=1111)
    result = generate_payment(payment, "CREDIT")
    assert result
    # make sure payment created
    payment = Payment.query.filter_by(amount=1111).first()
    assert payment

    payment = Payment(source_account="123456", to="123455", amount=-1112)
    result = generate_payment(payment, "DEBIT")
    assert result

    payment = Payment.query.filter_by(amount=-1112).first()
    assert payment
