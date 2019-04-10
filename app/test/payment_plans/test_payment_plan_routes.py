"""
    Test Payment Plan Routes
"""
import json

from unittest.mock import Mock, patch

from app.api.models import *
from app.test.base import BaseTestCase

class TestPaymentPlanRoutes(BaseTestCase):
    """ Test Payment Plan Routes"""

    def setUp(self):
        super().setUp()

        result = self.get_access_token("MODANAADMIN", "password")
        response = result.get_json()
        access_token = response["data"]["access_token"]

        self._token = access_token

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
    def test_create_payment_plan(self):
        """ test routes function to create payment plan """
        params = {
            "id" : "some-payment-plan-id",
            "destination" : "123456",
            "wallet_id" : self._wallet,
        }
        result = self.create_payment_plan(params, "some-api-key")
        response = result.get_json()
        self.assertTrue(response['data']['payment_plan_id'])
    # end def

    def test_get_payment_plans(self):
        """ test routes function to get payment plans"""
        params = {
            "id" : "some-payment-plan-id",
            "destination" : "123456",
            "wallet_id" : self._wallet,
        }
        result = self.create_payment_plan(params, "some-api-key")
        response = result.get_json()
        self.assertTrue(response['data']['payment_plan_id'])

        result = self.get_payment_plans("some-api-key")
        response = result.get_json()
        self.assertTrue(len(response['data']) > 0)
    # end def

    def test_get_payment_plans(self):
        """ test routes function to get payment plans"""
        params = {
            "id" : "some-payment-plan-id",
            "destination" : "123456",
            "wallet_id" : self._wallet,
        }
        result = self.create_payment_plan(params, "some-api-key")
        response = result.get_json()
        self.assertTrue(response['data']['payment_plan_id'])

        result = self.get_payment_plans("some-api-key")
        response = result.get_json()
        self.assertTrue(len(response['data']) > 0)
    # end def

    def test_get_payment_plan(self):
        """ test routes function to get payment plan"""
        params = {
            "id" : "some-payment-plan-id",
            "destination" : "123456",
            "wallet_id" : self._wallet,
        }
        result = self.create_payment_plan(params, "some-api-key")
        response = result.get_json()
        self.assertTrue(response['data']['payment_plan_id'])

        payment_plan_id = response['data']['payment_plan_id']

        result = self.get_payment_plan(payment_plan_id, "some-api-key")
        response = result.get_json()
        self.assertTrue(response['data'])
    # end def

    def test_remove_payment_plan(self):
        """ test routes function to get payment plan"""
        params = {
            "id" : "some-payment-plan-id",
            "destination" : "123456",
            "wallet_id" : self._wallet,
        }
        result = self.create_payment_plan(params, "some-api-key")
        response = result.get_json()
        self.assertTrue(response['data']['payment_plan_id'])

        payment_plan_id = response['data']['payment_plan_id']

        result = self.remove_payment_plan(payment_plan_id, "some-api-key")
        self.assertEqual(result.status_code, 204)
    # end def
# end cclass
