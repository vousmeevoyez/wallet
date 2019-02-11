"""
    Integration Testing between wallet & routes
"""
import json
from unittest.mock import Mock, patch

from app.test.base import BaseTestCase

# mock all response incoming from user services
from app.api.user.modules.user_services import UserServices
from app.api.user.modules.bank_account_services import BankAccountServices

from app.api.models import User
from app.api.models import Wallet
from app.api import db

from app.api.bank.bni.utility   import remote_call

from app.config import config

BASE_URL = "/api/v1"

BNI_ECOLLECTION_CONFIG = config.Config.BNI_ECOLLECTION_CONFIG


class TestCallbackRoutes(BaseTestCase):
    """ Test Class for Wallet Routes"""

    """
        HELPER function to request to specific URL
    """
    def deposit_callback(self, params):
        return self.client.post(
            BASE_URL + "/callback/bni_va/deposit",
            data=json.dumps(params),
            content_type="application/json"
        )

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
            BASE_URL + "/wallets/",
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
            BASE_URL + "/wallets/" + wallet_id,
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

    """
        DEPOSIT CALLBACK
    """
    def test_deposit_callback(self):
        """ DEPOSIT CALLBACK CASE 1 : Successfully deposit callback """
        access_token, user_id = self._create_dummy_user()

        params = {
            "user_id" : user_id,
            "access_token" : access_token,
            "label" : "wallet label",
            "pin" : "123456"
        }

        result = self.create_wallet(params, access_token)
        response = result.get_json()
        self.assertEqual(result.status_code, 201)

        user = User.query.filter_by(id=user_id).first()

        data = {
            "virtual_account"           : user.wallets[0].virtual_accounts[0].id,
            "customer_name"             : "jennie",
            "trx_id"                    : user.wallets[0].virtual_accounts[0].trx_id,
            "trx_amount"                : "0",
            "payment_amount"            : "50000",
            "cumulative_payment_amount" : "50000",
            "payment_ntb"               : "12345",
            "datetime_payment"          : "2018-12-20 11:16:00",
        }
        encrypted_data = remote_call.encrypt(BNI_ECOLLECTION_CONFIG["CREDIT_CLIENT_ID"], BNI_ECOLLECTION_CONFIG["CREDIT_SECRET_KEY"], data)

        expected_value = {
            "client_id" : BNI_ECOLLECTION_CONFIG["CREDIT_CLIENT_ID"],
            "data"      : encrypted_data.decode("UTF-8")
        }
        result = self.deposit_callback(expected_value)
        print(result.get_json())
