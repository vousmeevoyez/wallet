""" 
    Test Wallet Routes
"""
import json

from unittest.mock import Mock, patch

from app.test.base import BaseTestCase

# mock all response incoming from user services
from app.api.user.modules.user_services import UserServices
from app.api.user.modules.bank_account_services import BankAccountServices

BASE_URL = "/api/v1"
RESOURCE = "/wallets/"

class TestWalletRoutes(BaseTestCase):
    """ Test Class for Wallet Routes"""

    """
        HELPER function to request to specific URL
    """
    def get_access_token(self, username, password):
        """ get access token"""
        return self.client.post(
            BASE_URL + "/auth/" + "token",
            data=dict(
                username=username,
                password=password
            )
        )
    #end def

    def create_user(self, params, access_token):
        """ Create user """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.post(
            BASE_URL + "/users/",
            data=dict(
                username=params["username"],
                name=params["name"],
                phone_ext=params["phone_ext"],
                phone_number=params["phone_number"],
                email=params["email"],
                password=params["password"],
                pin=params["pin"],
                role=params["role"]
            ),
            headers=headers
        )
    #end def

    def create_wallet(self, params, access_token):
        """ Create wallet """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.post(
            BASE_URL + RESOURCE,
            data=dict(
                label=params["label"],
                pin=params["pin"]
            ),
            headers=headers
        )
    #end def

    def get_wallet_info(self, wallet_id, access_token):
        """ Create wallet """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.get(
            BASE_URL + RESOURCE + wallet_id,
            headers=headers
        )
    #end def

    def get_all_wallet(self, user_id, access_token):
        """ Create wallet """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.get(
            BASE_URL + RESOURCE + user_id,
            headers=headers
        )
    #end def

    def remove_wallet(self, wallet_id, access_token):
        """ remove wallet """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.delete(
            BASE_URL + RESOURCE + wallet_id,
            headers=headers
        )
    #end def

    def get_balance(self, wallet_id, access_token):
        """ get wallet balance """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.get(
            BASE_URL + RESOURCE + wallet_id + "/balance/",
            headers=headers
        )
    #end def

    def get_transaction(self, wallet_id, params, access_token):
        """ get wallet history """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.get(
            BASE_URL + RESOURCE + wallet_id +
            "/transactions?flag={}&start_date={}&end_date={}".format(params["flag"],
                                                                     params["start_date"],
                                                                     params["end_date"]),
            headers=headers
        )
    #end def

    def get_transaction_details(self, wallet_id, params, access_token):
        """ get wallet history details"""
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.get(
            BASE_URL + RESOURCE + wallet_id +
            "/transactions/{}".format(params["transaction_id"]),
            headers=headers
        )
    #end def

    def update_pin(self, wallet_id, params, access_token):
        """ update pin wallet """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.put(
            BASE_URL + RESOURCE + wallet_id + "/pin/",
            data=dict(
                old_pin=params["old_pin"],
                pin=params["pin"],
                confirm_pin=params["confirm_pin"]
            ),
            headers=headers
        )
    #end def

    def _create_dummy_user(self):
        params = {
            "username"     : "jennie",
            "name"         : "jennie",
            "phone_ext"    : "62",
            "phone_number" : "81219643444",
            "email"        : "jennie@blackpink.com",
            "password"     : "password",
            "pin"          : "123456",
            "role"         : "USER"
        }
        result = self.get_access_token("MODANAADMIN", "password")
        response = result.get_json()

        access_token = response["access_token"]

        result = self.create_user(params, access_token)
        response = result.get_json()["data"]
        return access_token, response["user_id"]

    def test_create_wallet(self):
        """ integration testing between walelt and user """

        access_token, user_id = self._create_dummy_user()

        params = {
            "user_id" : user_id,
            "access_token" : access_token,
            "label" : "wallet label",
            "pin" : "123456"
        }

        result = self.create_wallet(params, access_token)
        self.assertEqual(result.status_code, 201)

    def test_get_wallet_info(self):
        """ integration testing between walelt and user """

        access_token, user_id = self._create_dummy_user()

        params = {
            "access_token" : access_token,
            "label" : "wallet label",
            "pin" : "123456"
        }

        result = self.create_wallet(params, access_token)
        self.assertEqual(result.status_code, 201)

        response = result.get_json()
        wallet_id = response["data"]["wallet_id"]

        result = self.get_wallet_info(wallet_id, access_token)
        response = result.get_json()

        self.assertTrue(response["wallet"])

    def test_remove_wallet(self):
        """ integration testing between walelt and user """

        access_token, user_id = self._create_dummy_user()

        params = {
            "access_token" : access_token,
            "label" : "wallet label",
            "pin" : "123456"
        }

        result = self.create_wallet(params, access_token)
        self.assertEqual(result.status_code, 201)

        params = {
            "access_token" : access_token,
            "label" : "another label",
            "pin" : "123456"
        }

        result = self.create_wallet(params, access_token)
        self.assertEqual(result.status_code, 201)

        response = result.get_json()
        wallet_id = response["data"]["wallet_id"]

        result = self.get_all_wallet(str(user_id), access_token)

        #result = self.remove_wallet(wallet_id, access_token)

        #result = self.get_all_wallet(user_id, access_token)
        #print(result.get_json())

    def test_get_balance(self):
        """ integration testing between walelt and user """

        access_token, user_id = self._create_dummy_user()

        params = {
            "access_token" : access_token,
            "label" : "wallet label",
            "pin" : "123456"
        }

        result = self.create_wallet(params, access_token)
        self.assertEqual(result.status_code, 201)

        response = result.get_json()
        wallet_id = response["data"]["wallet_id"]

        result = self.get_balance(wallet_id, access_token)
        response = result.get_json()
        self.assertTrue(response["id"])

    def test_get_transactions(self):
        """ integration testing between walelt and user """

        access_token, user_id = self._create_dummy_user()

        params = {
            "access_token" : access_token,
            "label" : "wallet label",
            "pin" : "123456"
        }

        result = self.create_wallet(params, access_token)
        self.assertEqual(result.status_code, 201)

        response = result.get_json()
        wallet_id = response["data"]["wallet_id"]

        params = {
            "start_date" : "2019/01/01",
            "end_date"   : "2019/01/03",
            "flag" : "IN"
        }
        result = self.get_transaction(wallet_id, params, access_token)
        response = result.get_json()
        self.assertTrue(result.status_code, 200)

    def test_get_transactions_details(self):
        """ integration testing between walelt and user """

        access_token, user_id = self._create_dummy_user()

        params = {
            "access_token" : access_token,
            "label" : "wallet label",
            "pin" : "123456"
        }

        result = self.create_wallet(params, access_token)
        self.assertEqual(result.status_code, 201)

        response = result.get_json()
        wallet_id = response["data"]["wallet_id"]

        params = {
            "transaction_id" : "132456464",
        }
        result = self.get_transaction_details(wallet_id, params, access_token)
        response = result.get_json()
        self.assertTrue(result.status_code, 404)

    def test_update_pin_inccorrect_old_pin(self):
        """ integration testing between walelt and user """

        access_token, user_id = self._create_dummy_user()

        params = {
            "access_token" : access_token,
            "label" : "wallet label",
            "pin" : "123456"
        }

        result = self.create_wallet(params, access_token)
        self.assertEqual(result.status_code, 201)

        response = result.get_json()
        wallet_id = response["data"]["wallet_id"]

        params = {
            "old_pin"    : "111111",
            "pin"        : "123456",
            "confirm_pin": "123546",
        }
        result = self.update_pin(wallet_id, params, access_token)
        #print(result.get_json())
        self.assertEqual(result.status_code, 422)

    def test_update_pin_unmatch_pin(self):
        """ integration testing between walelt and user """

        access_token, user_id = self._create_dummy_user()

        params = {
            "access_token" : access_token,
            "label" : "wallet label",
            "pin" : "123456"
        }

        result = self.create_wallet(params, access_token)
        self.assertEqual(result.status_code, 201)

        response = result.get_json()
        wallet_id = response["data"]["wallet_id"]

        params = {
            "old_pin"    : "123456",
            "pin"        : "123456",
            "confirm_pin": "123546",
        }
        result = self.update_pin(wallet_id, params, access_token)
        #print(result.get_json())
        self.assertEqual(result.status_code, 422)

    def test_update_pin_old_pin(self):
        """ integration testing between walelt and user """

        access_token, user_id = self._create_dummy_user()

        params = {
            "access_token" : access_token,
            "label" : "wallet label",
            "pin" : "123456"
        }

        result = self.create_wallet(params, access_token)
        self.assertEqual(result.status_code, 201)

        response = result.get_json()
        wallet_id = response["data"]["wallet_id"]

        params = {
            "old_pin"    : "123456",
            "pin"        : "123456",
            "confirm_pin": "123456",
        }
        result = self.update_pin(wallet_id, params, access_token)
        self.assertEqual(result.status_code, 422)
