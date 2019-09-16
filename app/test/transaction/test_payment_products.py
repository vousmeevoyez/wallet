"""
    Test Payment Products
"""
from app.test.base import BaseTestCase

from app.api.models import Payment

from app.api.transactions.factories.payments.products import CreditPayment, DebitPayment


class TestPaymentProducts(BaseTestCase):
    def test_credit_payment(self):
        payment = Payment(source_account="123456", to="123455", amount=1000)

        credit_payment = CreditPayment()
        credit_payment.load(payment)

        result = credit_payment.create()
        self.assertTrue(result)

    def test_debit_payment(self):
        payment = Payment(source_account="123456", to="123455", amount=-1000)

        debit_payment = DebitPayment()
        debit_payment.load(payment)

        result = debit_payment.create()
        self.assertTrue(result)
