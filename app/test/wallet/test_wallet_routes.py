"""
    Integration Testing between wallet & routes
"""
from unittest.mock import Mock, patch

from app.test.base import BaseTestCase

# mock all response incoming from user services
from app.api.user.modules.user_services import UserServices
from app.api.user.modules.bank_account_services import BankAccountServices

from app.api.models import User
from app.api.models import Wallet
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

    def get_all_wallet(self, access_token):
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

    def bank_transfer(self, source, destination, params, access_token):
        """ Api Call for transfer between wallet """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.post(
            BASE_URL + RESOURCE + "{}/transfer/bank/{}".format(source, destination),
            data=dict(
                amount=params["amount"],
                pin=params["pin"],
                notes=params["notes"]
            ),
            headers=headers
        )
    #end def

    def forgot_pin(self, source, access_token):
        """ Api Call for forgot wallet pin"""
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.get(
            BASE_URL + RESOURCE + "{}/forgot/".format(source),
            headers=headers
        )
    #end def

    def verify_forgot_pin(self, source, params, access_token):
        """ Api Call for verify forgot wallet pin"""
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.post(
            BASE_URL + RESOURCE + "{}/forgot/".format(source),
            data=dict(
                otp_key=params["otp_key"],
                otp_code=params["otp_code"],
                pin=params["pin"],
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

    def qr_transfer(self, source, params, access_token):
        """ Api Call for QR transfer between wallet """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.post(
            BASE_URL + RESOURCE + "{}/qr/transfer".format(source),
            data=dict(
                qr_string=params["qr_string"],
                pin=params["pin"],
                amount=params["amount"]
            ),
            headers=headers
        )
    #end def

    def get_qr(self, wallet_id, access_token):
        """ Api Call for getting qr string """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.get(
            BASE_URL + RESOURCE + wallet_id + "/qr/",
            headers=headers
        )
    #end def

    def create_user_bank_account(self, user_id, params, access_token):
        """ add userbank account """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.post(
            BASE_URL + "/users/"+ user_id + "/bank_account/",
            data=dict(
                account_no=params["account_no"],
                label=params["label"],
                name=params["name"],
                bank_code=params["bank_code"]
            ),
            headers=headers
        )
    #ende def

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
        print(result)
        response = result.get_json()["data"]

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
        self.assertEqual(response["error"], "DUPLICATE_WALLET")
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

        result = self.get_all_wallet(access_token)

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
        self.assertEqual(response["error"], "ONLY_WALLET")
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

    def test_get_transactions_serialize_failed(self):
        """ GET TRANSACTIONS CASE 2 : Get wallet transaction with invalid
        payload """
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
            "start_date" : "2019-01-01",
            "end_date"   : "2019-01-03",
            "flag" : "KLK"
        }
        result = self.get_transaction(wallet_id, params, access_token)
        response = result.get_json()
        self.assertTrue(result.status_code, 400)

    def test_get_transactions_invalid_wallet(self):
        """ GET TRANSACTIONS CASE 3 : Get wallet transaction with invalid
        wallet"""
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
            "flag" : "ALL"
        }
        result = self.get_transaction(wallet_id, params, access_token)
        response = result.get_json()
        self.assertTrue(result.status_code, 404)

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

        # inject balance
        wallet = Wallet.query.get(source)
        wallet.balance = 99999999
        db.session.commit()

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
        self.assertEqual(result.status_code, 202)

    def test_transfer_locked_source(self):
        """ CASE 2 Transfer : but wallet is locked"""
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

        # inject balance
        wallet = Wallet.query.get(source)
        wallet.lock()
        db.session.commit()

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
        response = result.get_json()
        self.assertEqual(result.status_code, 422)
        self.assertTrue(response["error"], "WALLET_LOCKED")

    def test_transfer_incorrect_pin(self):
        """ CASE 3 Transfer : try transfer with invalid pin"""
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

        # inject balance
        wallet = Wallet.query.get(source)
        wallet.balance = 99999999
        db.session.commit()

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
            "pin" : "111111"
        }

        result = self.transfer(str(source), str(destination), params,
                               access_token)
        response = result.get_json()

        self.assertEqual(result.status_code, 422)
        self.assertTrue(response["error"], "INCORRECT_PIN")

    def test_transfer_invalid_destination(self):
        """ CASE 4 Transfer : try transfer with same between source """
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

        # inject balance
        wallet = Wallet.query.get(source)
        wallet.balance = 99999999
        db.session.commit()

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

        result = self.transfer(str(source), str(source), params,
                               access_token)
        response = result.get_json()
        self.assertEqual(result.status_code, 422)

    """
        QR Code
    """
    def test_get_qr(self):
        """ GET_QR CASE 1 : return qr string"""
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

        result = self.get_qr(wallet_id, access_token)
        response = result.get_json()
        self.assertEqual(result.status_code, 200)
        self.assertTrue(response["qr_string"])
    """
        FOrgot pin
    """
    def test_forgot_pin(self):
        """ FORGOT PIN CASE 1 : send forgot otp"""
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

        result = self.forgot_pin(wallet_id, access_token)
        response = result.get_json()

        self.assertEqual(result.status_code, 201)
        self.assertTrue(response["data"])
        self.assertTrue(response["data"]["otp_key"])
        self.assertTrue(response["data"]["otp_code"])

    def test_forgot_pin_pending(self):
        """ FORGOT PIN CASE 2 : send forgot otp there's pending """
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

        result = self.forgot_pin(wallet_id, access_token)
        response = result.get_json()

        self.assertEqual(result.status_code, 201)
        self.assertTrue(response["data"])
        self.assertTrue(response["data"]["otp_key"])
        self.assertTrue(response["data"]["otp_code"])

        result = self.forgot_pin(wallet_id, access_token)
        response = result.get_json()
        self.assertEqual(result.status_code, 422)
        self.assertEqual(response["error"], "PENDING_OTP")


    """
        Verify Forgot OTP
    """
    def test_verify_forgot_pin(self):
        """ VERIFY FORGOT PIN CASE 1 : verify forgot otp"""
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

        result = self.forgot_pin(wallet_id, access_token)
        response = result.get_json()

        self.assertEqual(result.status_code, 201)
        self.assertTrue(response["data"])
        self.assertTrue(response["data"]["otp_key"])
        self.assertTrue(response["data"]["otp_code"])

        otp_key = response["data"]["otp_key"]
        otp_code = response["data"]["otp_code"]

        params = {
            "otp_key" : otp_key,
            "otp_code": otp_code,
            "pin" : "12345"
        }

        result = self.verify_forgot_pin(wallet_id, params, access_token)
        self.assertEqual(result.status_code, 204)

    def test_verify_forgot_pin_not_found(self):
        """ VERIFY FORGOT PIN CASE 2 : verify forgot otp not found """
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

        result = self.forgot_pin(wallet_id, access_token)
        response = result.get_json()

        self.assertEqual(result.status_code, 201)
        self.assertTrue(response["data"])
        self.assertTrue(response["data"]["otp_key"])
        self.assertTrue(response["data"]["otp_code"])

        params = {
            "otp_key" : "12312312312",
            "otp_code": "123456",
            "pin" : "12345"
        }

        result = self.verify_forgot_pin(wallet_id, params, access_token)
        print(result.get_json())
        self.assertEqual(result.status_code, 404)

    """
        WITHDRAW 
    """
    def test_withdraw(self):
        """ CASE 1 Withdraw : try success withdraw """
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

        # inject balance
        wallet = Wallet.query.get(source)
        wallet.balance = 99999999
        db.session.commit()

        params = {
            "amount" : "50000",
            "pin" : "123456"
        }

        result = self.withdraw(str(source), params,
                               access_token)
        response = result.get_json()
        self.assertEqual(result.status_code, 200)
        self.assertTrue(response["valid_until"])
        self.assertTrue(response["amount"])

    def test_withdraw_all(self):
        """ CASE 2 Withdraw : try success withdraw all """
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

        # inject balance
        wallet = Wallet.query.get(source)
        wallet.balance = 99999999
        db.session.commit()

        params = {
            "amount" : "0",
            "pin" : "123456"
        }

        result = self.withdraw(str(source), params,
                               access_token)
        response = result.get_json()

        self.assertEqual(result.status_code, 200)
        self.assertTrue(response["valid_until"])
        self.assertTrue(response["amount"])

    """
        BANK TRANSFER 
    """
    def test_bank_transfer(self):
        """ CASE 1 Bank Transfer : successfully bank transfer """
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

        # inject balance
        wallet = Wallet.query.get(source)
        wallet.balance = 99999999
        db.session.commit()

        # add account bank information
        params = {
            "account_no": "3333333333",
            "name"      : "Bpk KEN AROK",
            "label"     : "Irene Bank Account",
            "bank_code" : "014"
        }
        result = self.create_user_bank_account(str(user_id), params, access_token)
        response = result.get_json()

        bank_account_id = response["data"]["bank_account_id"]

        params = {
            "amount" : "15",
            "notes" : "some notes",
            "pin" : "123456"
        }

        result = self.bank_transfer(str(source), str(bank_account_id), params,
                                    access_token)
        self.assertEqual(result.status_code, 202)

    def test_bank_transfer_bank_account_not_found(self):
        """ CASE 2 Bank Transfer invalid bank account id: successfully bank transfer """
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

        # inject balance
        wallet = Wallet.query.get(source)
        wallet.balance = 99999999
        db.session.commit()

        # add account bank information
        params = {
            "account_no": "3333333333",
            "name"      : "Bpk KEN AROK",
            "label"     : "Irene Bank Account",
            "bank_code" : "014"
        }
        result = self.create_user_bank_account(str(user_id), params, access_token)
        response = result.get_json()

        bank_account_id = response["data"]["bank_account_id"]

        params = {
            "amount" : "15",
            "notes" : "some notes",
            "pin" : "123456"
        }

        result = self.bank_transfer(str(source), "12345", params,
                                    access_token)
        self.assertEqual(result.status_code, 404)

    """
        QR TRANSFER
    """
    def test_qr_transfer(self):
        """ CASE 1 QR Transfer : successfully transfer """
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

        # inject balance
        wallet = Wallet.query.get(source)
        wallet.balance = 99999999
        db.session.commit()

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

        result = self.get_qr(destination, access_token)
        response = result.get_json()
        self.assertEqual(result.status_code, 200)
        self.assertTrue(response["qr_string"])

        params = {
            "qr_string" : response["qr_string"],
            "amount" : "15",
            "pin" : "123456"
        }

        result = self.qr_transfer(str(source), params, access_token)
        self.assertEqual(result.status_code, 202)

    def test_qr_transfer_invalid_qr(self):
        """ CASE 2 QR Transfer : try transfer using invalid QR """
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

        # inject balance
        wallet = Wallet.query.get(source)
        wallet.balance = 99999999
        db.session.commit()

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

        result = self.get_qr(destination, access_token)
        response = result.get_json()
        self.assertEqual(result.status_code, 200)
        self.assertTrue(response["qr_string"])

        params = {
            "qr_string" : "aksjdlajsldjkasjldjaklsjdlajsjdajsdjasl",
            "amount" : "15",
            "pin" : "123456"
        }

        result = self.qr_transfer(str(source), params, access_token)
        response = result.get_json()
        self.assertEqual(result.status_code, 400)
        self.assertTrue(response["error"])
        self.assertTrue(response["message"])
