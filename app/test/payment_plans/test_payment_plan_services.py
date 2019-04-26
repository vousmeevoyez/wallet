"""
    Test Payment Plan Services
"""
import uuid
from datetime import datetime
from unittest.mock import patch, Mock

from app.api import db

from app.test.base  import BaseTestCase

from app.api.models import *

from app.api.payment_plans.modules.payment_plan_services import \
PaymentPlanServices

# exceptions
from app.api.error.http import *

from task.bank.tasks import BankTask

class TestPaymentPlan(BaseTestCase):
    """ Test Class for Payment Plan """

    def setUp(self):
        super().setUp()

        source_wallet = Wallet(user_id=self.user.id)
        source_wallet.set_pin("123456")
        db.session.add(source_wallet)
        db.session.commit()

        self.wallet = source_wallet

    def test_add(self):
        """ test method for adding payment plan and plan """
        plans = []
        plan = Plan(
            amount=100,
            due_date=datetime(2019, 1, 5)
        )

        plan2 = Plan(
            amount=100,
            due_date=datetime(2019, 2, 1)
        )
        plans.append(plan)
        plans.append(plan2)

        payment_plan = PaymentPlan(
            destination="some-bank-account-number",
            plans=plans
        )

        result = PaymentPlanServices(str(self.wallet.id)).add(payment_plan)
        self.assertEqual(result[1], 201)
        self.assertTrue(result[0]['data']['payment_plan_id'])

        plans = []
        plan = Plan(
            amount=100,
            due_date=datetime(2019, 1, 3)
        )

        plan2 = Plan(
            amount=100,
            due_date=datetime(2019, 2, 4)
        )
        plans.append(plan)
        plans.append(plan2)

        payment_plan_id = 'some-payment-plan-id'
        payment_plan = PaymentPlan(
            id=payment_plan_id,
            destination="some-bank-account-number",
            plans=plans
        )

        result = PaymentPlanServices(str(self.wallet.id)).add(payment_plan)
        self.assertEqual(result[1], 201)
        self.assertEqual(result[0]['data']['payment_plan_id'], payment_plan_id)

    def test_add_but_auto_pay(self):
        """ test method for adding payment plan and plan but repayment using
        auto pay """
        plans = []
        plan = Plan(
            amount=100,
            due_date=datetime(2019, 1, 5)
        )

        plan2 = Plan(
            amount=100,
            due_date=datetime(2019, 2, 1)
        )
        plans.append(plan)
        plans.append(plan2)

        payment_plan = PaymentPlan(
            destination="some-bank-account-number",
            plans=plans,
            method=2 # mark payment as auto pay
        )

        result = PaymentPlanServices(str(self.wallet.id)).add(payment_plan)
        self.assertEqual(result[1], 201)
        self.assertTrue(result[0]['data']['payment_plan_id'])

        plans = []
        plan = Plan(
            amount=100,
            due_date=datetime(2019, 1, 3)
        )

        plan2 = Plan(
            amount=100,
            due_date=datetime(2019, 2, 4)
        )
        plans.append(plan)
        plans.append(plan2)

        payment_plan_id = 'some-payment-plan-id'
        payment_plan = PaymentPlan(
            id=payment_plan_id,
            destination="some-bank-account-number",
            plans=plans
        )

        result = PaymentPlanServices(str(self.wallet.id)).add(payment_plan)
        self.assertEqual(result[1], 201)
        self.assertEqual(result[0]['data']['payment_plan_id'], payment_plan_id)

    def test_add_bank_account_already_exist(self):
        """ test method for adding payment plan and plan """
        plans = []
        plan = Plan(
            amount=100,
            due_date=datetime(2019, 1, 1)
        )

        plan2 = Plan(
            amount=100,
            due_date=datetime(2019, 2, 1)
        )
        plans.append(plan)
        plans.append(plan2)

        payment_plan = PaymentPlan(
            destination="some-bank-account-number",
            plans=plans
        )

        result = PaymentPlanServices(str(self.wallet.id)).add(payment_plan)
        self.assertEqual(result[1], 201)
        self.assertTrue(result[0]['data']['payment_plan_id'])

        payment_plan_id = 'some-payment-plan-id'
        payment_plan = PaymentPlan(
            id=payment_plan_id,
            destination="some-bank-account-number",
            plans=plans
        )

        result = PaymentPlanServices(str(self.wallet.id)).add(payment_plan)
        self.assertEqual(result[1], 201)
        self.assertEqual(result[0]['data']['payment_plan_id'], payment_plan_id)

    def test_show(self):
        """ test method for showing all payment plan """
        plans = []
        plan = Plan(
            amount=100,
            due_date=datetime(2019, 1, 1)
        )

        plan2 = Plan(
            amount=100,
            due_date=datetime(2019, 2, 1)
        )
        plans.append(plan)
        plans.append(plan2)

        payment_plan = PaymentPlan(
            destination="some-bank-account-number",
            plans=plans
        )

        result = PaymentPlanServices(str(self.wallet.id)).add(payment_plan)
        self.assertEqual(result[1], 201)
        self.assertTrue(result[0]['data']['payment_plan_id'])


        result = PaymentPlanServices.show()
        self.assertTrue(len(result[0]['data']) > 0)

    def test_info(self):
        """ test method for single payment plan """
        plans = []
        plan = Plan(
            amount=100,
            due_date=datetime(2019, 1, 1)
        )

        plan2 = Plan(
            amount=100,
            due_date=datetime(2019, 2, 1)
        )
        plans.append(plan)
        plans.append(plan2)

        payment_plan = PaymentPlan(
            destination="some-bank-account-number",
            plans=plans
        )

        result = PaymentPlanServices(str(self.wallet.id)).add(payment_plan)
        self.assertEqual(result[1], 201)
        self.assertTrue(result[0]['data']['payment_plan_id'])

        payment_plan_id = result[0]['data']['payment_plan_id']
        result = PaymentPlanServices(payment_plan_id=payment_plan_id).info()
        self.assertTrue(result[0]['data'])

    def test_remove(self):
        """ test method for removing payment plan """
        plans = []
        plan = Plan(
            amount=100,
            due_date=datetime(2019, 1, 1)
        )

        plan2 = Plan(
            amount=100,
            due_date=datetime(2019, 2, 1)
        )
        plans.append(plan)
        plans.append(plan2)

        payment_plan = PaymentPlan(
            destination="some-bank-account-number",
            plans=plans
        )

        result = PaymentPlanServices(str(self.wallet.id)).add(payment_plan)
        self.assertEqual(result[1], 201)
        self.assertTrue(result[0]['data']['payment_plan_id'])

        payment_plan_id = result[0]['data']['payment_plan_id']
        result = PaymentPlanServices(payment_plan_id=payment_plan_id).remove()
        self.assertEqual(result[1], 204)

    def test_update(self):
        """ test method for updating payment plan """
        plans = []
        plan = Plan(
            amount=100,
            due_date=datetime(2019, 1, 1)
        )

        plan2 = Plan(
            amount=100,
            due_date=datetime(2019, 2, 1)
        )
        plans.append(plan)
        plans.append(plan2)

        payment_plan = PaymentPlan(
            destination="some-bank-account-number",
            plans=plans
        )

        result = PaymentPlanServices(str(self.wallet.id)).add(payment_plan)
        self.assertEqual(result[1], 201)
        self.assertTrue(result[0]['data']['payment_plan_id'])
        payment_plan_id = result[0]['data']['payment_plan_id']

        params = {
            "destination" : "123123123123",
            "status" : False
        }
        result = PaymentPlanServices(
            payment_plan_id=payment_plan_id,
            wallet_id=str(self.wallet.id)
        ).update(params)
        self.assertEqual(result[1], 204)

