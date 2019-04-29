"""
    Integration Testing between wallet & routes
"""
from datetime import datetime, timedelta
import uuid
from unittest.mock import Mock, patch

from app.test.base import BaseTestCase

from app.api.models import User
from app.api.models import Wallet
from app.api import db

class TestAutoPayRoutes(BaseTestCase):
    """ Test Class for Wallet Routes"""
    def setUp(self):
        super().setUp()

        self._api_key = "8c574c41-3e01-4763-89af-fd370989da33"

        result = self.get_access_token("MODANAADMIN", "password")
        response = result.get_json()

        access_token = response["data"]["access_token"]

        self._token = access_token
        user1, wallet1 = self._create_dummy_user()
        user2, wallet2 = self._create_dummy_user2()
        self._user1 = user1
        self._wallet1 = wallet1

        self._user2 = user2
        self._wallet2 = wallet2
    #end def

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

    def _create_dummy_user2(self):
        params = {
            "username"     : "lisalisalisa",
            "name"         : "lisalisalisa",
            "phone_ext"    : "62",
            "phone_number" : "81219643999",
            "email"        : "lisalisalisa@blackpink.com",
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
        TRANSFER 
    """
    def test_transfer(self):
        """ CASE 1 Transfer : successfully transfer """
        # inject balance
        wallet = Wallet.query.get(self._wallet1)
        wallet.balance = 99999999
        db.session.commit()

        # create payment plan
        due_date = datetime.utcnow().replace(hour=0, minute=1, second=0)
        plans = [{
            "amount" : "1000000",
            "type" : "MAIN",
            "due_date" : due_date.isoformat()
        }]

        params = {
            "destination" : "123456",
            "method" : "AUTO",
            "wallet_id" : self._wallet2,
            "plans" : plans
        }
        result = self.create_payment_plan(params, self._api_key)
        response = result.get_json()
        print(response)

        params = {
            "amount": "1000000",
            "notes" : "payroll disburse",
            "pin"   : "123456",
            "types" : "PAYROLL"
        }

        result = self.transfer(self._wallet1, self._wallet2, params,
                               self._token)
        response = result.get_json()
        self.assertEqual(result.status_code, 202)
        self.assertTrue(response["data"])

        # TEST GETTING IN TRANSACTION
        params = {
            "start_date" : "2019/04/28",
            "end_date"   : "2019/04/29",
            "flag" : "ALL"
        }
        result = self.get_transaction(self._wallet2, params, self._token)
        response = result.get_json()
        print(response)
        self.assertTrue(result.status_code, 200)
