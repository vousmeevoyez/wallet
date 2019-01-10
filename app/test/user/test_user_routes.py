""" 
    Test User Routes
"""
import json

from unittest.mock import Mock, patch

from app.test.base import BaseTestCase

# mock all response incoming from user services
from app.api.user.modules.user_services import UserServices
from app.api.user.modules.bank_account_services import BankAccountServices

BASE_URL = "/api/v1"
RESOURCE = "/users/"

class TestUserRoutes(BaseTestCase):
    """ Test Class for User Routes"""

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
            BASE_URL + RESOURCE,
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

    def get_all_user(self, access_token):
        """ get all user """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.get(
            BASE_URL + RESOURCE,
            headers=headers
        )
    #end def

    def get_user(self, user_id, access_token):
        """ get user """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.get(
            BASE_URL + RESOURCE + user_id,
            headers=headers
        )
    #end def

    def create_user_bank_account(self, user_id, params, access_token):
        """ add userbank account """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.post(
            BASE_URL + RESOURCE + user_id + "/bank_account/",
            data=dict(
                account_no=params["account_no"],
                label=params["label"],
                name=params["name"],
                bank_code=params["bank_code"]
            ),
            headers=headers
        )
    #ende def

    def get_bank_account(self, user_id, access_token):
        """ get user """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.get(
            BASE_URL + RESOURCE + user_id + "/bank_account/",
            headers=headers
        )
    #end def

    def remove_bank_account(self, user_id, bank_account_id, access_token):
        """ remove user bank account"""
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.delete(
            BASE_URL + RESOURCE + user_id + "/bank_account/" + bank_account_id,
            headers=headers
        )
    #end def

    def update_bank_account(self, user_id, bank_account_id, params, access_token):
        """ update userbank account """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.put(
            BASE_URL + RESOURCE + user_id + "/bank_account/" + bank_account_id,
            data=dict(
                account_no=params["account_no"],
                label=params["label"],
                name=params["name"],
                bank_code=params["bank_code"]
            ),
            headers=headers
        )
    #ende def

    """
        TEST BEGIN HERE 
    """

    @patch.object(UserServices, "add")
    def test_create_user_routes_success(self, mock_user_services):
        """ test routes function to create user"""
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
        access_token = response["data"]["access_token"]

        expected_value = {
            "message" : "some message",
            "data" : "some data"
        }

        mock_user_services.return_value = expected_value
        result = self.create_user(params, access_token)
        response = result.get_json()

        self.assertEqual(response, expected_value)

    def test_create_user_routes_failed_validate_input(self):
        """ test routes function to create user but there are some invalid data
        passed to this routes"""
        params = {
            "username"     : "",
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
        access_token = response["data"]["access_token"]

        result = self.create_user(params, access_token)
        status_code = result.status_code

        self.assertEqual(status_code, 400) # bad request

    @patch.object(UserServices, "show")
    def test_get_all_user(self, mock_user_services):
        """ test method that return all user """
        result = self.get_access_token("MODANAADMIN", "password")
        response = result.get_json()
        access_token = response["data"]["access_token"]


        mock_user_services.return_value = {
            "data" : "some data"
        }
        result = self.get_all_user(access_token)
        status_code = result.status_code

        self.assertEqual(status_code, 200) # ok

    @patch.object(UserServices, "info")
    def test_get_user(self, mock_user_services):
        """ test method that get user info"""
        result = self.get_access_token("MODANAADMIN", "password")
        response = result.get_json()
        access_token = response["data"]["access_token"]

        mock_user_services.return_value = {
            "data" : "some data"
        }
        result = self.get_user("1", access_token)
        status_code = result.status_code

        self.assertEqual(status_code, 200) # ok

    @patch.object(BankAccountServices, "add")
    def test_create_user_bank_account_success(self, mock_bank_account_services):
        """ test method that get user info"""
        # get access token first
        result = self.get_access_token("MODANAADMIN", "password")
        response = result.get_json()
        access_token = response["data"]["access_token"]

        params = {
            "account_no": "3333333333",
            "name"      : "Bpk KEN AROK",
            "label"     : "Irene Bank Account",
            "bank_code" : "014"
        }

        # mock response here
        mock_bank_account_services.return_value = {
            "data" : "some data"
        }
        result = self.create_user_bank_account("1", params, access_token)
        status_code = result.status_code

        self.assertEqual(status_code, 200) # ok

    def test_create_user_bank_account_validate_failed(self):
        """ test method that get user info but failed because some invalid
        input"""
        # get access token first
        result = self.get_access_token("MODANAADMIN", "password")
        response = result.get_json()
        access_token = response["data"]["access_token"]

        params = {
            "account_no": "",
            "name"      : "Bpk KEN AROK",
            "label"     : "Irene Bank Account",
            "bank_code" : "014"
        }

        result = self.create_user_bank_account("1", params, access_token)
        status_code = result.status_code

        self.assertEqual(status_code, 400) # ok

    @patch.object(BankAccountServices, "show")
    def test_get_user_bank_account(self, mock_bank_account_services):
        """ test routes that return bank account information"""
        # get access token first
        result = self.get_access_token("MODANAADMIN", "password")
        response = result.get_json()
        access_token = response["data"]["access_token"]

        # mock function
        mock_bank_account_services.return_value = {"data" : "Some data"}
        result = self.get_bank_account("1", access_token)
        status_code = result.status_code

        self.assertEqual(status_code, 200) # ok

    @patch.object(BankAccountServices, "remove")
    def test_remove_bank_account(self, mock_bank_account_services):
        """ test routes that remove bank account"""
        # get access token first
        result = self.get_access_token("MODANAADMIN", "password")
        response = result.get_json()
        access_token = response["data"]["access_token"]

        # mock function
        mock_bank_account_services.return_value = {"data" : "Some data"}
        result = self.remove_bank_account("1", "1", access_token)
        status_code = result.status_code

        self.assertEqual(status_code, 200) # ok

    @patch.object(BankAccountServices, "update")
    def test_update_user_bank_account_success(self, mock_bank_account_services):
        """ test method that update user bank account information"""
        # get access token first
        result = self.get_access_token("MODANAADMIN", "password")
        response = result.get_json()
        access_token = response["data"]["access_token"]

        params = {
            "account_no": "3333333333",
            "name"      : "Bpk KEN AROK",
            "label"     : "Irene Bank Account",
            "bank_code" : "014"
        }

        # mock response here
        mock_bank_account_services.return_value = {
            "data" : "some data"
        }
        result = self.update_bank_account("1", "1", params, access_token)
        status_code = result.status_code

        self.assertEqual(status_code, 200) # ok
