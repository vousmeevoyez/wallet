"""
    Test Plan Services
"""
import uuid
from datetime import datetime
from unittest.mock import patch, Mock

from app.api import db

from app.test.base  import BaseTestCase

from app.api.models import *

from app.api.plans.modules.plan_services import PlanServices

# exceptions
from app.api.error.http import *

class TestPlan(BaseTestCase):
    """ Test Class for Plan """
    def setUp(self):
        super().setUp()

        source_wallet = Wallet(user_id=self.user.id)
        source_wallet.set_pin("123456")
        db.session.add(source_wallet)
        db.session.commit()

        self.wallet = source_wallet

    def test_add(self):
        """ test method for plan """
        payment_plan = PaymentPlan(
            id="some-payment-plan-id",
            wallet_id=self.wallet.id,
            destination="some-bank-account-number",
        )
        db.session.add(payment_plan)
        db.session.commit()

        plan = Plan(
            amount=1000,
            due_date=datetime(2019, 4, 25)
        )

        result = PlanServices(payment_plan_id=payment_plan.id).add(plan)
        self.assertEqual(result[1], 201)
        self.assertTrue(result[0]['data']['plan_id'])

        plan = Plan(
            id="some-plan-id",
            amount=1000,
            due_date=datetime(2019, 5, 25)
        )

        result = PlanServices(payment_plan_id=payment_plan.id).add(plan)
        self.assertEqual(result[1], 201)
        self.assertEqual(result[0]['data']['plan_id'], "some-plan-id")

    def test_add_auto_pay(self):
        """ test method for adding plan but setting auto pay"""
        payment_plan = PaymentPlan(
            id="some-payment-plan-id",
            wallet_id=self.wallet.id,
            method=2, # set to auto pay
            destination="some-bank-account-number",
        )
        db.session.add(payment_plan)
        db.session.commit()

        plan = Plan(
            amount=1000,
            type=1, # additional
            due_date=datetime(2019, 4, 25)
        )

        result = PlanServices(payment_plan_id=payment_plan.id).add(plan)
        self.assertEqual(result[1], 201)
        self.assertTrue(result[0]['data']['plan_id'])

    def test_show(self):
        """ test method for showing plan """
        payment_plan = PaymentPlan(
            id="some-payment-plan-id",
            wallet_id=self.wallet.id,
            destination="some-bank-account-number",
        )
        db.session.add(payment_plan)
        db.session.commit()

        plan = Plan(
            amount=1000,
            due_date=datetime(2019, 4, 25)
        )

        result = PlanServices(payment_plan_id=payment_plan.id).add(plan)
        self.assertEqual(result[1], 201)
        self.assertTrue(result[0]['data']['plan_id'])

        result = PlanServices.show()
        self.assertTrue(result[0]['data'])

    def test_info(self):
        """ test method for info plan """
        payment_plan = PaymentPlan(
            id="some-payment-plan-id",
            wallet_id=self.wallet.id,
            destination="some-bank-account-number",
        )
        db.session.add(payment_plan)
        db.session.commit()

        plan = Plan(
            amount=1000,
            due_date=datetime(2019, 4, 25)
        )

        result = PlanServices(payment_plan_id=payment_plan.id).add(plan)
        self.assertEqual(result[1], 201)
        self.assertTrue(result[0]['data']['plan_id'])

        plan_id = result[0]['data']['plan_id']

        result = PlanServices(plan_id=plan_id).info()
        self.assertTrue(result[0]['data'])

    def test_update(self):
        """ test method for info plan """
        payment_plan = PaymentPlan(
            id="some-payment-plan-id",
            wallet_id=self.wallet.id,
            destination="some-bank-account-number",
        )
        db.session.add(payment_plan)
        db.session.commit()

        plan = Plan(
            amount=1000,
            due_date=datetime(2019, 4, 25)
        )

        result = PlanServices(payment_plan_id=payment_plan.id).add(plan)
        self.assertEqual(result[1], 201)
        self.assertTrue(result[0]['data']['plan_id'])

        plan_id = result[0]['data']['plan_id']


        plan = Plan(
            amount=1111,
            due_date=datetime(2019, 3, 25)
        )

        result = PlanServices(plan_id=plan_id).update(plan)
        self.assertTrue(result[1], 204)

    def test_update_status(self):
        """ test method for info plan """
        payment_plan = PaymentPlan(
            id="some-payment-plan-id",
            wallet_id=self.wallet.id,
            destination="some-bank-account-number",
        )
        db.session.add(payment_plan)
        db.session.commit()

        plan = Plan(
            amount=1000,
            due_date=datetime(2019, 4, 25)
        )

        result = PlanServices(payment_plan_id=payment_plan.id).add(plan)
        self.assertEqual(result[1], 201)
        self.assertTrue(result[0]['data']['plan_id'])

        plan_id = result[0]['data']['plan_id']

        result = PlanServices(plan_id=plan_id).update_status({"status" :
                                                              "PENDING"})
        self.assertTrue(result[1], 204)

        result = PlanServices(plan_id=plan_id).update_status({"status" :
                                                              "RETRYING"})
        self.assertTrue(result[1], 204)

        result = PlanServices(plan_id=plan_id).update_status({"status" :
                                                              "PAID"})
        self.assertTrue(result[1], 204)

        result = PlanServices(plan_id=plan_id).update_status({"status" :
                                                              "SENDING"})
        self.assertTrue(result[1], 204)

        result = PlanServices(plan_id=plan_id).update_status({"status" :
                                                              "FAIL"})
        self.assertTrue(result[1], 204)

    def test_remove(self):
        """ test method for remove plan """
        payment_plan = PaymentPlan(
            id="some-payment-plan-id",
            wallet_id=self.wallet.id,
            destination="some-bank-account-number",
        )
        db.session.add(payment_plan)
        db.session.commit()

        plan = Plan(
            amount=1000,
            due_date=datetime(2019, 4, 25)
        )

        result = PlanServices(payment_plan_id=payment_plan.id).add(plan)
        self.assertEqual(result[1], 201)
        self.assertTrue(result[0]['data']['plan_id'])

        plan_id = result[0]['data']['plan_id']

        result = PlanServices(plan_id=plan_id).remove()
        self.assertTrue(result[1], 204)
