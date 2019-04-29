"""
    Test Payment Plan Routes
"""
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from app.api.models import *
from app.test.base import BaseTestCase

class TestPlanRoutes(BaseTestCase):
    """ Test Payment Plan Routes"""

    def setUp(self):
        super().setUp()

        result = self.get_access_token("MODANAADMIN", "password")
        response = result.get_json()

        access_token = response["data"]["access_token"]
        self._token = access_token

        # api key
        self._api_key = "8c574c41-3e01-4763-89af-fd370989da33"

        user, wallet = self._create_dummy_user()
        self._wallet = wallet

    def _create_dummy_user(self):
        params = {
            "username"     : "roseroserose",
            "name"         : "roseroserose",
            "phone_ext"    : "62",
            "phone_number" : "81219642666",
            "email"        : "roseroserose@blackpink.com",
            "password"     : "password",
            "pin"          : "123456",
            "role"         : "USER"
        }
        result = self.create_user(params, self._token)
        response = result.get_json()["data"]
        user_id = response["user_id"]
        wallet_id = response["wallet_id"]
        return user_id, wallet_id

    """
        TEST BEGIN HERE 
    """
    def test_create_plan_auto(self):
        """ test routes function to create payment plan """
        params = {
            "id" : "some-payment-plan-id",
            "method" : "AUTO",
            "destination" : "123456",
            "wallet_id" : self._wallet,
        }
        result = self.create_payment_plan(params, self._api_key)
        response = result.get_json()
        self.assertTrue(response['data']['payment_plan_id'])

        payment_plan_id = response['data']['payment_plan_id']

        due_date = datetime.utcnow()
        params = {
            "payment_plan_id" : payment_plan_id,
            "amount" : "1000",
            "type" : "MAIN",
            "due_date" : due_date.isoformat()
        }
        result = self.create_plan(params, self._api_key)
        response = result.get_json()
        self.assertTrue(response['data']['plan_id'])

        due_date = datetime.utcnow() + timedelta(minutes=1)
        params = {
            "payment_plan_id" : payment_plan_id,
            "amount" : "1000",
            "type" : "ADDITIONAL",
            "due_date" : due_date.isoformat()
        }
        result = self.create_plan(params, self._api_key)
        response = result.get_json()
        plan_id = response['data']['plan_id']
        self.assertTrue(response['data']['plan_id'])

        result = self.get_plan(plan_id, self._api_key)
        print(result.get_json())

        params = {
            "method" : "AUTO_PAY",
            "destination" : "123456",
            "wallet_id" : self._wallet,
        }
        result = self.create_payment_plan(params, self._api_key)
        response = result.get_json()
        self.assertTrue(response['data']['payment_plan_id'])

        payment_plan_id = response['data']['payment_plan_id']

        due_date = datetime.utcnow()
        params = {
            "payment_plan_id" : payment_plan_id,
            "amount" : "1000",
            "type" : "MAIN",
            "due_date" : due_date.isoformat()
        }
        result = self.create_plan(params, self._api_key)
        response = result.get_json()
        self.assertTrue(response['data']['plan_id'])

        due_date = datetime.utcnow() + timedelta(minutes=1)
        params = {
            "payment_plan_id" : payment_plan_id,
            "amount" : "1000",
            "type" : "ADDITIONAL",
            "due_date" : due_date.isoformat()
        }
        result = self.create_plan(params, self._api_key)
        response = result.get_json()
        plan_id = response['data']['plan_id']
        self.assertTrue(response['data']['plan_id'])

        result = self.get_plan(plan_id, self._api_key)
        print(result.get_json())

        params = {
            "method" : "AUTO_DEBIT",
            "destination" : "123456",
            "wallet_id" : self._wallet,
        }
        result = self.create_payment_plan(params, self._api_key)
        response = result.get_json()
        self.assertTrue(response['data']['payment_plan_id'])

        payment_plan_id = response['data']['payment_plan_id']

        due_date = datetime.utcnow()
        params = {
            "payment_plan_id" : payment_plan_id,
            "amount" : "1000",
            "type" : "MAIN",
            "due_date" : due_date.isoformat()
        }
        result = self.create_plan(params, self._api_key)
        response = result.get_json()
        self.assertTrue(response['data']['plan_id'])

        due_date = datetime.utcnow() + timedelta(minutes=1)
        params = {
            "payment_plan_id" : payment_plan_id,
            "amount" : "1000",
            "type" : "ADDITIONAL",
            "due_date" : due_date.isoformat()
        }
        result = self.create_plan(params, self._api_key)
        response = result.get_json()
        plan_id = response['data']['plan_id']
        self.assertTrue(response['data']['plan_id'])

        result = self.get_plan(plan_id, self._api_key)
        print(result.get_json())
    # end def

    def test_update_plan(self):
        """ test routes function to update plan """
        params = {
            "id" : "some-payment-plan-id",
            "destination" : "123456",
            "wallet_id" : self._wallet,
        }
        result = self.create_payment_plan(params, self._api_key)
        response = result.get_json()
        self.assertTrue(response['data']['payment_plan_id'])

        payment_plan_id = response['data']['payment_plan_id']

        params = {
            "payment_plan_id" : payment_plan_id,
            "amount" : "1000",
            "type" : "MAIN",
            "due_date" : "2020-12-12"
        }
        result = self.create_plan(params, self._api_key)
        response = result.get_json()
        self.assertTrue(response['data']['plan_id'])

        plan_id = response['data']['plan_id']

        params = {
            "payment_plan_id" : payment_plan_id,
            "amount" : "1000",
            "type" : "MAIN",
            "due_date" : "2020-12-12"
        }
        result = self.update_plan(plan_id, params, self._api_key)
        self.assertEqual(result.status_code, 204)
    # end def

    def test_update_plan_status(self):
        """ test routes function to update plan """
        params = {
            "id" : "some-payment-plan-id",
            "destination" : "123456",
            "wallet_id" : self._wallet,
        }
        result = self.create_payment_plan(params, self._api_key)
        response = result.get_json()
        self.assertTrue(response['data']['payment_plan_id'])

        payment_plan_id = response['data']['payment_plan_id']

        params = {
            "payment_plan_id" : payment_plan_id,
            "amount" : "1000",
            "type" : "MAIN",
            "due_date" : "2020-12-12"
        }
        result = self.create_plan(params, self._api_key)
        response = result.get_json()
        self.assertTrue(response['data']['plan_id'])

        plan_id = response['data']['plan_id']

        params = {
            "status" : "PAID",
        }
        result = self.update_plan_status(plan_id, params, self._api_key)
        self.assertEqual(result.status_code, 204)

        params = {
            "status" : "FAILED",
        }
        result = self.update_plan_status(plan_id, params, self._api_key)
        self.assertEqual(result.status_code, 204)

        params = {
            "status" : "STOPPED",
        }
        result = self.update_plan_status(plan_id, params, self._api_key)
        self.assertEqual(result.status_code, 204)

        result = self.get_plan(plan_id, self._api_key)
        response = result.get_json()
        self.assertEqual(response["data"]["status"], params["status"])
    # end def
