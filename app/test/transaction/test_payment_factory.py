"""
    Test Payment Products
"""
from app.test.base import BaseTestCase

from app.api.models import Payment

from app.api.transactions.factories.payments.factory import generate_payment


class TestPaymentProducts(BaseTestCase):
    def test_generate_payment(self):
        payment = Payment(source_account="123456", to="123455", amount=1000)
        result = generate_payment(payment, "CREDIT")
        print(result.id)
        self.assertTrue(result)

        payment = Payment(source_account="123456", to="123455", amount=-1000)
        result = generate_payment(payment, "DEBIT")
        print(result.id)
        self.assertTrue(result)
