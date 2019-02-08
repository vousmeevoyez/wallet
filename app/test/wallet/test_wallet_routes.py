"""
    Integration Testing between wallet & routes
"""
from unittest.mock import Mock, patch

from app.test.base import BaseTestCase

# mock all response incoming from user services
from app.api.user.modules.user_services import UserServices
from app.api.user.modules.bank_account_services import BankAccountServices

from app.api.models import User
from app.api import db

BASE_URL = "/api/v1"
RESOURCE = "/wallets/"

class TestWalletRoutes(BaseTestCase):
    """ Test Class for Wallet Routes"""

    """
        HELPER function to request to specific URL
    """
    def get_access_token(self, username, password):
        """ Api Call for get Access Token """
        return self.client.post(
            BASE_URL + "/auth/" + "token",
            data=dict(
                username=username,
                password=password
            )
        )
    #end def

    def create_user(self, params, access_token):
        """ Api Call for Creating User """
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
        """ Api Call for Creating Wallet """
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
        """ Api Call for getting wallet info"""
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.get(
            BASE_URL + RESOURCE + wallet_id,
            headers=headers
        )
    #end def

    def get_all_wallet(self, user_id, access_token):
        """ Api Call for show all wallet that user have"""
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.get(
            BASE_URL + RESOURCE,
            headers=headers
        )
    #end def

    def remove_wallet(self, wallet_id, access_token):
        """ Remove Wallet """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.delete(
            BASE_URL + RESOURCE + wallet_id,
            headers=headers
        )
    #end def

    def get_balance(self, wallet_id, access_token):
        """ Api Call for getting balance """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.get(
            BASE_URL + RESOURCE + wallet_id + "/balance/",
            headers=headers
        )
    #end def

    def get_transaction(self, wallet_id, params, access_token):
        """ Api Call for getting wallet transaction """
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
        """ Api Call for getting wallet transaction details """
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
        """ Api Call for updating pin """
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

    def transfer(self, source, destination, params, access_token):
        """ Api Call for transfer between wallet """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.post(
            BASE_URL + RESOURCE + "{}/transfer/{}".format(source, destination),
            data=dict(
                amount=params["amount"],
                pin=params["pin"],
                notes=params["notes"]
            ),
            headers=headers
        )
    #end def

    def withdraw(self, source, params, access_token):
        """ Api Call for withdraw wallet """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.post(
            BASE_URL + RESOURCE + "{}/withdraw/".format(source),
            data=dict(
                amount=params["amount"],
                pin=params["pin"]
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

        user = User.query.get(response["user_id"])
        user.balance = 999999
        db.session.commit()

        return access_token, response["user_id"]

    def _create_dummy_user2(self):
        params = {
            "username"     : "jisooo",
            "name"         : "jisooo",
            "phone_ext"    : "62",
            "phone_number" : "81219644444",
            "email"        : "jisooo@blackpink.com",
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

    """
        CREATE WALLET
    """
    def test_create_wallet(self):
        """ CREATE_WALLET CASE 1 : Successfully created wallet """
        access_token, user_id = self._create_dummy_user()

        params = {
            "user_id" : user_id,
            "access_token" : access_token,
            "label" : "wallet label",
            "pin" : "123456"
        }

        result = self.create_wallet(params, access_token)
        self.assertEqual(result.status_code, 201)

    def test_create_wallet_duplicate(self):
        """ CREATE_WALLET CASE 2 : Failed created wallet because some entry not unique """
        access_token, user_id = self._create_dummy_user()

        params = {
            "user_id" : user_id,
            "access_token" : access_token,
            "label" : "wallet label",
            "pin" : "123456"
        }

        result = self.create_wallet(params, access_token)
        self.assertEqual(result.status_code, 201)

        params = {
            "user_id" : user_id,
            "access_token" : access_token,
            "label" : "wallet label",
            "pin" : "123456"
        }

        result = self.create_wallet(params, access_token)
        response = result.get_json()

        self.assertEqual(result.status_code, 422)
        self.assertEqual(response["error"], "WALLET_ALREADY_EXISTED")
        self.assertTrue(response["message"])

    def test_create_wallet_serialize_error(self):
        """ CREATE_WALLET CASE 3 : Failed created wallet because some invalid payload """
        access_token, user_id = self._create_dummy_user()

        params = {
            "user_id" : user_id,
            "access_token" : access_token,
            "label" : "wallet_label", # ALPHABET ONLY
            "pin" : "1" # PIN TOO SHOORT
        }

        result = self.create_wallet(params, access_token)
        response = result.get_json()
        self.assertEqual(result.status_code, 400)
        self.assertEqual(response["error"], "INVALID_PARAMETER")
        self.assertTrue(response["details"])

    """
        WALLET INFO
    """
    def test_get_wallet_info(self):
        """ GET_WALLET_INFO CASE 1 : Successfully get wallet information """
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

    def test_get_wallet_info_not_found(self):
        """ GET_WALLET_INFO CASE 2 : Failed get wallet information because
        error not found"""
        access_token, user_id = self._create_dummy_user()

        result = self.get_wallet_info("12345", access_token)
        response = result.get_json()

        self.assertEqual(result.status_code, 404) # not found
        self.assertEqual(response["error"], "WALLET_NOT_FOUND")
        self.assertTrue(response["message"])

    """ 
        REMOVE WALLET
    """

    def test_remove_wallet(self):
        """ REMOVE WALLET CASE 1 : Successfully remove wallet """
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
            "label" : "wallet lllabel",
            "pin" : "123456"
        }

        result = self.create_wallet(params, access_token)
        self.assertEqual(result.status_code, 201)

        response = result.get_json()
        wallet_id = response["data"]["wallet_id"]

        result = self.remove_wallet(wallet_id, access_token)
        self.assertEqual(result.status_code, 204)

        result = self.get_all_wallet(str(user_id), access_token)

    def test_remove_wallet_failed(self):
        """ REMOVE WALLET CASE 2 : Failed remove wallet because only wallet """
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

        result = self.remove_wallet(wallet_id, access_token)
        response = result.get_json()

        self.assertEqual(result.status_code, 422)
        self.assertEqual(response["error"], "ERROR_REMOVING_WALLET")
        self.assertTrue(response["message"])

    """
        GET BALANCE
    """
    def test_get_balance(self):
        """ GET_BALAANCE CASE 1 : return wallet balance information """
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

    def test_get_balance_wallet_not_found(self):
        """ GET_BALANCE CASE 2 : check wallet balance information but with
        invalid wallet"""
        access_token, user_id = self._create_dummy_user()

        wallet_id = "1233232"
        result = self.get_balance(wallet_id, access_token)
        response = result.get_json()

        self.assertEqual(result.status_code, 404) # not found
        self.assertEqual(response["error"], "WALLET_NOT_FOUND")
        self.assertTrue(response["message"])

    """
        GET TRANSACTIONS
    """
    def test_get_transactions(self):
        """ GET TRANSACTIONS CASE 1 : Get wallet transaction for specific date"""
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

        # TEST GETTING IN TRANSACTION
        params = {
            "start_date" : "2019/01/01",
            "end_date"   : "2019/01/03",
            "flag" : "IN"
        }
        result = self.get_transaction(wallet_id, params, access_token)
        response = result.get_json()
        self.assertTrue(result.status_code, 200)

        # TEST GETTING OUT TRANSACTION
        params = {
            "start_date" : "2019/01/01",
            "end_date"   : "2019/01/03",
            "flag" : "OUT"
        }
        result = self.get_transaction(wallet_id, params, access_token)
        response = result.get_json()
        self.assertTrue(result.status_code, 200)
        
        #TEST GETTING ALL TRANSACTIONS
        params = {
            "start_date" : "2019/01/01",
            "end_date"   : "2019/01/03",
            "flag" : "ALL"
        }
        result = self.get_transaction(wallet_id, params, access_token)
        response = result.get_json()
        self.assertTrue(result.status_code, 200)

    """
        TRANSACTION DETAILS
    """
    def test_get_transactions_details(self):
        """ GET TRANSACTIONS DETAILS 1 : Get wallet transaction details but
        transaction not found"""
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
        self.assertEqual(response["error"], "TRANSACTION_NOT_FOUND")
        self.assertTrue(response["message"])

    """ 
        UPDATE PIN
    """
    def test_update_pin_incorrect_old_pin(self):
        """CASE 1 UPDATE PIN : Incorrect old pin"""
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
        response = result.get_json()
        self.assertEqual(result.status_code, 422)
        self.assertTrue(response["error"])

    def test_update_pin_unmatch_pin(self):
        """ CASE 2 UPDATE PIN : unmatch pin """
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
        """ CASE 3 UPDATE PIN : old pin """
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

    """ 
        TRANSFER
    """
    def test_transfer(self):
        """ CASE 1 Transfer : successfully transfer """
        access_token, user_id = self._create_dummy_user()

        params = {
            "access_token" : access_token,
            "label" : "wallet label",
            "pin" : "123456"
        }

        result = self.create_wallet(params, access_token)
        self.assertEqual(result.status_code, 201)

        response = result.get_json()
        source = response["data"]["wallet_id"]

        access_token, user_id = self._create_dummy_user2()

        params = {
            "access_token" : access_token,
            "label" : "jisoo wallet",
            "pin" : "123456"
        }

        result = self.create_wallet(params, access_token)
        self.assertEqual(result.status_code, 201)

        response = result.get_json()
        destination = response["data"]["wallet_id"]

        params = {
            "amount" : "15",
            "notes" : "some notes",
            "pin" : "123456"
        }

        result = self.transfer(str(source), str(destination), params,
                               access_token)
        print(result.get_json())
