""" 
    Test User Routes
"""
import json

from unittest.mock import Mock, patch

from app.api.models import *
from app.test.base import BaseTestCase

# mock all response incoming from user services
from app.api.users.modules.user_services import UserServices
from app.api.users.modules.bank_account_services import BankAccountServices

BASE_URL = "/api/v1"
RESOURCE = "/users/"


class TestUserRoutes(BaseTestCase):
    """ Test Class for User Routes"""

    def setUp(self):
        super().setUp()

        user_id, wallet_id = self.create_dummy_user(self.access_token)
        self.user_id = user_id
        self.wallet_id = wallet_id

    # end def

    """
        TEST BEGIN HERE 
    """

    def test_create_user_routes_success(self):
        """ test routes function to create user"""
        params = {
            "username": "jennie",
            "name": "jennie",
            "phone_ext": "62",
            "phone_number": "81219643444",
            "email": "jennie@blackpink.com",
            "password": "password",
            "pin": "123456",
            "role": "USER",
            "label": "PERSONAL",
        }
        result = self.create_user(params, self.access_token)
        response = result.get_json()["data"]

        self.assertTrue(response["user_id"])

    def test_create_user_routes_failed_validate_input(self):
        """ test routes function to create user but there are some invalid data
        passed to this routes"""
        params = {
            "username": "",
            "name": "jennie",
            "phone_ext": "62",
            "phone_number": "81219643444",
            "email": "jennie@blackpink.com",
            "password": "password",
            "pin": "123456",
            "role": "USER",
            "label": "PERSONAL",
        }
        result = self.create_user(params, self.access_token)
        self.assertEqual(result.status_code, 400)  # bad request

    def test_get_all_user(self):
        """ test method that return all user """
        result = self.get_all_user(self.access_token)
        status_code = result.status_code
        response = result.get_json()

        self.assertEqual(status_code, 200)  # ok

    def test_update_user(self):
        """ test routes function to update user"""
        params = {
            "username": "jennie",
            "name": "jennie",
            "phone_ext": "62",
            "phone_number": "81219643444",
            "email": "jennie@blackpink.com",
            "password": "password",
            "pin": "123456",
            "role": "USER",
            "label": "PERSONAL",
        }
        result = self.create_user(params, self.access_token)
        response = result.get_json()["data"]

        user_id = response["user_id"]

        params = {
            "name": "jennai",
            "phone_ext": "62",
            "phone_number": "81219644444",
            "email": "jennie@blckpink.com",
            "password": "password",
        }
        result = self.update_user(params, user_id, self.access_token)
        self.assertEqual(result.status_code, 204)

    def test_get_user(self):
        """ test method that get user info"""
        result = self.get_user(self.user_id, self.access_token)
        self.assertEqual(result.status_code, 200)  # ok

    def test_create_user_bank_account_success(self):
        """ test method that get user info"""
        # get access token first
        params = {
            "account_no": "3333333333",
            "name": "Bpk KEN AROK",
            "label": "Irene Bank Account",
            "bank_code": "014",
        }

        result = self.create_user_bank_account(self.user_id, params, self.access_token)
        self.assertEqual(result.status_code, 201)  # created

    def test_create_user_bank_account_validate_failed(self):
        """ test method that get user info but failed because some invalid
        input"""
        params = {
            "account_no": "",
            "name": "Bpk KEN AROK",
            "label": "Irene Bank Account",
            "bank_code": "014",
        }

        result = self.create_user_bank_account(self.user_id, params, self.access_token)
        self.assertEqual(result.status_code, 400)  # ok

        params = {
            "account_no": "123132123132131",
            "name": "aaaaaaaaaaaaaa aaaaaaaaaa aaaaaaaaaaaa\
            aaaaaaaaaaaaaaaaaaaaaaaaaa",
            "label": "Irene Bank Account",
            "bank_code": "014",
        }

        result = self.create_user_bank_account(self.user_id, params, self.access_token)
        self.assertEqual(result.status_code, 400)  # ok

    def test_get_user_bank_account(self):
        """ test routes that return bank account information"""
        params = {
            "account_no": "3333333333",
            "name": "Bpk KEN AROK",
            "label": "Irene Bank Account",
            "bank_code": "014",
        }

        result = self.create_user_bank_account(self.user_id, params, self.access_token)
        status_code = result.status_code

        result = self.get_bank_account(self.user_id, self.access_token)
        self.assertEqual(result.status_code, 200)  # ok

    def test_remove_bank_account(self):
        """ test routes that remove bank account"""
        # get access token first
        params = {
            "account_no": "3333333333",
            "name": "Bpk KEN AROK",
            "label": "Irene Bank Account",
            "bank_code": "014",
        }

        result = self.create_user_bank_account(self.user_id, params, self.access_token)
        self.assertEqual(result.status_code, 201)  # ok

        bank_account_id = result.get_json()["data"]["bank_account_id"]

        result = self.remove_bank_account(
            self.user_id, bank_account_id, self.access_token
        )
        self.assertEqual(result.status_code, 204)  # no content

    def test_update_user_bank_account_success(self):
        """ test method that update user bank account information"""
        params = {
            "account_no": "3333333333",
            "name": "Bpk KEN AROK",
            "label": "Irene Bank Account",
            "bank_code": "014",
        }

        result = self.create_user_bank_account(self.user_id, params, self.access_token)
        self.assertEqual(result.status_code, 201)  # ok

        bank_account_id = result.get_json()["data"]["bank_account_id"]

        # get access token first
        params = {
            "account_no": "1111333333",
            "name": "Bpk KEN AROK",
            "label": "Kelvin Bank Accounts",
            "bank_code": "014",
        }
        result = self.update_bank_account(
            self.user_id, bank_account_id, params, self.access_token
        )
        status_code = result.status_code

        self.assertEqual(status_code, 204)  # ok
