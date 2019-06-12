"""
    Test Payment Plan Routes
"""
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from app.api.models import *
from app.test.base import BaseTestCase

class TestPaymentPlanRoutes(BaseTestCase):
    """ Test Payment Plan Routes"""

    def setUp(self):
        super().setUp()

        # api key
        self._api_key = "8c574c41-3e01-4763-89af-fd370989da33"

        user_id, wallet_id = self.create_dummy_user(self.access_token)
        self.user_id = user_id
        self.wallet_id = wallet_id
    # end def

    """
        TEST BEGIN HERE 
    """
    def test_create_payment_plan(self):
        """ test routes function to create payment plan """
        due_date = datetime.utcnow()
        plans = [{
            "amount" : "1000",
            "type" : "MAIN",
            "due_date" : due_date.isoformat()
        }]

        params = {
            "destination" : "123456",
            "method" : "AUTO_PAY",
            "wallet_id" : self.wallet_id,
            "plans" : plans
        }
        # create payment plan here
        result = self.create_payment_plan(params, self._api_key)
        response = result.get_json()
        payment_plan_id = response['data']['payment_plan_id']
        self.assertTrue(response['data']['payment_plan_id'])

        # make sure payment plan created here
        result = self.get_payment_plan(payment_plan_id, self._api_key)
        response = result.get_json()

        due_date = datetime.utcnow()
        plans = [{
            "amount" : "1000",
            "type" : "MAIN",
            "due_date" : due_date.isoformat()
        }]

        params = {
            "destination" : "123456",
            "method" : "AUTO_DEBIT",
            "wallet_id" : self.wallet_id,
            "plans" : plans
        }
        # create payment plan here
        result = self.create_payment_plan(params, self._api_key)
        response = result.get_json()
        self.assertTrue(response['data']['payment_plan_id'])

        # make sure payment plan created
        payment_plan_id = response['data']['payment_plan_id']
        result = self.get_payment_plan(payment_plan_id, self._api_key)
        response = result.get_json()

        due_date = datetime.utcnow()
        plans = [{
            "amount" : "1000",
            "type" : "MAIN",
            "due_date" : due_date.isoformat()
        }]

        params = {
            "destination" : "123456",
            "method" : "AUTO",
            "wallet_id" : self.wallet_id,
            "plans" : plans
        }
        result = self.create_payment_plan(params, self._api_key)
        response = result.get_json()
        self.assertTrue(response['data']['payment_plan_id'])
        payment_plan_id = response['data']['payment_plan_id']
        result = self.get_payment_plan(payment_plan_id, self._api_key)
        response = result.get_json()
    # end def

    def test_get_payment_plans(self):
        """ test routes function to get payment plans"""
        params = {
            "id" : "some-payment-plan-id",
            "destination" : "123456",
            "method" : "AUTO_PAY",
            "wallet_id" : self.wallet_id,
        }
        result = self.create_payment_plan(params, self._api_key)
        response = result.get_json()
        self.assertTrue(response['data']['payment_plan_id'])

        result = self.get_payment_plans(self._api_key)
        response = result.get_json()
        self.assertTrue(len(response['data']) > 0)
    # end def

    def test_get_payment_plan(self):
        """ test routes function to get payment plan"""
        params = {
            "id" : "some-payment-plan-id",
            "destination" : "123456",
            "method" : "AUTO_PAY",
            "wallet_id" : self.wallet_id,
        }
        result = self.create_payment_plan(params, self._api_key)
        response = result.get_json()
        self.assertTrue(response['data']['payment_plan_id'])

        payment_plan_id = response['data']['payment_plan_id']

        result = self.get_payment_plan(payment_plan_id, self._api_key)
        response = result.get_json()
        self.assertTrue(response['data'])
    # end def

    def test_remove_payment_plan(self):
        """ test routes function to get payment plan"""
        params = {
            "id" : "some-payment-plan-id",
            "destination" : "123456",
            "method" : "AUTO_PAY",
            "wallet_id" : self.wallet_id,
        }
        result = self.create_payment_plan(params, self._api_key)
        response = result.get_json()
        self.assertTrue(response['data']['payment_plan_id'])

        payment_plan_id = response['data']['payment_plan_id']

        result = self.remove_payment_plan(payment_plan_id, self._api_key)
        self.assertEqual(result.status_code, 204)

        params = {
            "id" : "some-payment-plan-id",
            "destination" : "123456",
            "method" : "AUTO_PAY",
            "wallet_id" : self.wallet_id,
        }
        result = self.create_payment_plan(params, self._api_key)
        response = result.get_json()
        self.assertTrue(response['data']['payment_plan_id'])
    # end def

    def test_update_payment_plan(self):
        """ test routes function to update payment plan"""
        params = {
            "id" : "some-payment-plan-id",
            "destination" : "123456",
            "method" : "AUTO_PAY",
            "wallet_id" : self.wallet_id,
        }
        result = self.create_payment_plan(params, self._api_key)
        response = result.get_json()
        self.assertTrue(response['data']['payment_plan_id'])

        payment_plan_id = response['data']['payment_plan_id']

        params = {
            "destination" : "654321",
            "wallet_id" : self.wallet_id,
            "method" : "AUTO_PAY",
            "status" : "DEACTIVE",
        }
        result = self.update_payment_plan(payment_plan_id, params, self._api_key)
        self.assertEqual(result.status_code, 204)

        result = self.get_payment_plan(payment_plan_id, self._api_key)
        response = result.get_json()
    # end def
# end class