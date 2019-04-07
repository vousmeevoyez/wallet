"""
    Integration Testing between wallet & routes
"""
import uuid
from unittest.mock import Mock, patch

from app.test.base import BaseTestCase

from app.api.models import User
from app.api.models import Wallet
from app.api import db

class TestWalletRoutes(BaseTestCase):
    """ Test Class for Wallet Routes"""
    def setUp(self):
        super().setUp()

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

    '''
    """
        GET TRANSACTIONS
    """
    def test_get_transactions(self):
        """ GET TRANSACTIONS CASE 1 : Get wallet transaction for specific date"""
        # TEST GETTING IN TRANSACTION
        params = {
            "start_date" : "2019/01/01",
            "end_date"   : "2019/01/03",
            "flag" : "IN"
        }
        result = self.get_transaction(self._wallet1, params, self._token)
        response = result.get_json()
        self.assertTrue(result.status_code, 200)
        # TEST GETTING OUT TRANSACTION
        params = {
            "start_date" : "2019/01/01",
            "end_date"   : "2019/01/03",
            "flag" : "OUT"
        }
        result = self.get_transaction(self._wallet1, params, self._token)
        response = result.get_json()
        self.assertTrue(result.status_code, 200)
        #TEST GETTING ALL TRANSACTIONS
        params = {
            "start_date" : "2019/01/01",
            "end_date"   : "2019/01/03",
            "flag" : "ALL"
        }
        result = self.get_transaction(self._wallet1, params, self._token)
        response = result.get_json()
        self.assertTrue(result.status_code, 200)

    def test_get_transactions_serialize_failed(self):
        """ GET TRANSACTIONS CASE 2 : Get wallet transaction with invalid
        payload """
        # TEST GETTING IN TRANSACTION
        params = {
            "start_date" : "2019-01-01",
            "end_date"   : "2019-01-03",
            "flag" : "KLK"
        }
        result = self.get_transaction(self._wallet1, params, self._token)
        response = result.get_json()
        self.assertTrue(result.status_code, 400)

    """
        TRANSACTION DETAILS
    """
    def test_get_transactions_details(self):
        """ GET TRANSACTIONS DETAILS 1 : Get wallet transaction details but
        transaction not found"""
        params = {
            "transaction_id" : str(uuid.uuid4()),
        }
        result = self.get_transaction_details(self._wallet1, params, self._token)
        response = result.get_json()
        self.assertTrue(result.status_code, 404)
        self.assertEqual(response["error"], "TRANSACTION_NOT_FOUND")
        self.assertTrue(response["message"])
    '''
    """
        REFUND
    """
    def test_refund_transfer(self):
        """ CASE 1 Refund : successfully refund a transfer """
        # inject balance
        wallet = Wallet.query.get(self._wallet1)
        wallet.balance = 99999999
        db.session.commit()

        params = {
            "amount" : "15",
            "notes" : "some notes",
            "pin" : "123456",
            "types": "PAYROLL"
        }

        result = self.transfer(
            self._wallet1, self._wallet2,
            params, self._token
        )
        response = result.get_json()

        self.assertEqual(result.status_code, 202)
        self.assertTrue(response["data"])

        # get transaction id that going to be refunded
        transaction_id = response["data"]["id"]

        result = self.refund_transaction(transaction_id, self._token)
        response = result.get_json()

        self.assertEqual(result.status_code, 202)
        self.assertTrue(response["data"])
