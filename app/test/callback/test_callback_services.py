import json

from app.test.base  import BaseTestCase
from app.api.models import *

from app.api.callback.modules.callback_services import CallbackServices

BASE_URL = "/api/v1"

class TestCallbackServices(BaseTestCase):

    def get_access_token(self, username, password):
        """ function to get access token using auth url"""
        return self.client.post(
            BASE_URL + "/auth/" + "token",
            data=dict(
                username=username,
                password=password
            )
        )
    #end def

    def create_user(self, params, access_token):
        """ function to create user using user api"""
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
                role=params["role"],
            ),
            headers=headers
        )
    #end def

    def test_create_payment(self):
        """ test function to create payment"""
        params = {
            "payment_channel_key" : "BNI_VA",
            "source_account"      : "123456",
            "to"                  : "123457",
            "reference_number"    : "111111",
            "payment_amount"      : 1,
            "payment_type"        : True,
        }
        result = CallbackServices()._create_payment(params)
        self.assertTrue(result > 0)
    #end def

    def test_inject_success(self):
        """ test function to successfully inject balance"""
        # get admin access token first
        result = self.get_access_token("MODANAADMIN", "password")
        response = result.get_json()
        access_token = response["data"]["access_token"]

        # create dummy user here
        params = {
            "username"     : "jennie",
            "name"         : "jennie",
            "phone_ext"    : "62",
            "phone_number" : "81219643444",
            "email"        : "jennie@bp.com",
            "password"     : "password",
            "pin"          : "123456",
            "role"         : "USER"
        }
        result = self.create_user(params, access_token)
        response = result.get_json()

        user_id = response["data"]["user_id"]
        wallet_id = response["data"]["wallet_id"]

        params = {
            "payment_channel_key" : "BNI_VA",
            "source_account"      : "123456",
            "to"                  : "123457",
            "reference_number"    : "111111",
            "payment_amount"      : 1,
            "payment_type"        : True,
        }
        payment_id = CallbackServices()._create_payment(params)

        params = {
            "payment_id": payment_id,
            "wallet_id" : wallet_id,
            "amount"    : 1111,
        }
        result = CallbackServices()._inject(params)
        self.assertEqual(result["status"], "SUCCESS")

        # make sure balance injected successfully
        wallet = Wallet.query.filter_by(id=wallet_id).first()
        self.assertEqual(wallet.balance, params["amount"])

    def test_inject_failed_invalid_amount_less_than_zero(self):
        """ test function to failed inject balance because amount is less than
        zero"""
        # get admin access token first
        result = self.get_access_token("MODANAADMIN", "password")
        response = result.get_json()
        access_token = response["data"]["access_token"]

        # create dummy user here
        params = {
            "username"     : "jennie",
            "name"         : "jennie",
            "phone_ext"    : "62",
            "phone_number" : "81219643444",
            "email"        : "jennie@bp.com",
            "password"     : "password",
            "pin"          : "123456",
            "role"         : "USER"
        }
        result = self.create_user(params, access_token)
        response = result.get_json()

        user_id = response["data"]["user_id"]
        wallet_id = response["data"]["wallet_id"]

        params = {
            "payment_channel_key" : "BNI_VA",
            "source_account"      : "123456",
            "to"                  : "123457",
            "reference_number"    : "111111",
            "payment_amount"      : -1111,
            "payment_type"        : True,
        }
        payment_id = CallbackServices()._create_payment(params)

        params = {
            "payment_id": payment_id,
            "wallet_id" : wallet_id,
            "amount"    : -1111,
        }
        result = CallbackServices()._inject(params)
        self.assertEqual(result["status"], "FAILED")

    def test_inject_failed_wallet_not_found(self):
        """ test function to failed injct balance because the wallet is not
        found"""
        # get admin access token first
        result = self.get_access_token("MODANAADMIN", "password")
        response = result.get_json()
        access_token = response["data"]["access_token"]

        # create dummy user here
        params = {
            "username"     : "jennie",
            "name"         : "jennie",
            "phone_ext"    : "62",
            "phone_number" : "81219643444",
            "email"        : "jennie@bp.com",
            "password"     : "password",
            "pin"          : "123456",
            "role"         : "USER"
        }
        result = self.create_user(params, access_token)
        response = result.get_json()

        user_id = response["data"]["user_id"]
        wallet_id = response["data"]["wallet_id"]

        params = {
            "payment_channel_key" : "BNI_VA",
            "source_account"      : "123456",
            "to"                  : "123457",
            "reference_number"    : "111111",
            "payment_amount"      : -1111,
            "payment_type"        : True,
        }
        payment_id = CallbackServices()._create_payment(params)

        params = {
            "payment_id": payment_id,
            "wallet_id" : "66666666",
            "amount"    : -1111,
        }
        result = CallbackServices()._inject(params)
        self.assertEqual(result["status"], "FAILED")

    def test_deduct_success(self):
        """ test function to successfully deduct balance"""
        # get admin access token first
        result = self.get_access_token("MODANAADMIN", "password")
        response = result.get_json()
        access_token = response["data"]["access_token"]

        # create dummy user here
        params = {
            "username"     : "jennie",
            "name"         : "jennie",
            "phone_ext"    : "62",
            "phone_number" : "81219643444",
            "email"        : "jennie@bp.com",
            "password"     : "password",
            "pin"          : "123456",
            "role"         : "USER"
        }
        result = self.create_user(params, access_token)
        response = result.get_json()

        user_id = response["data"]["user_id"]
        wallet_id = response["data"]["wallet_id"]

        params = {
            "payment_channel_key" : "BNI_VA",
            "source_account"      : "123456",
            "to"                  : "123457",
            "reference_number"    : "111111",
            "payment_amount"      : 1,
            "payment_type"        : True,
        }
        payment_id = CallbackServices()._create_payment(params)

        params = {
            "payment_id": payment_id,
            "wallet_id" : wallet_id,
            "amount"    : 1111,
        }
        result = CallbackServices()._inject(params)
        self.assertEqual(result["status"], "SUCCESS")

        # make sure balance injected successfully
        wallet = Wallet.query.filter_by(id=wallet_id).first()
        self.assertEqual(wallet.balance, params["amount"])

        # deduct everything here
        params = {
            "payment_channel_key" : "BNI_VA",
            "source_account"      : "123456",
            "to"                  : "123457",
            "reference_number"    : "111112",
            "payment_amount"      : -11,
            "payment_type"        : False,
        }
        payment_id = CallbackServices()._create_payment(params)

        params = {
            "payment_id": payment_id,
            "wallet_id" : wallet_id,
            "amount"    : -11,
        }
        result = CallbackServices()._deduct(params)
        self.assertEqual(result["status"], "SUCCESS")

        # make sure balance injected successfully
        wallet = Wallet.query.filter_by(id=wallet_id).first()
        self.assertEqual(wallet.balance, 1100)

    def test_deposit_success(self):
        """ test function to successfully deposit balance"""
        # get admin access token first
        result = self.get_access_token("MODANAADMIN", "password")
        response = result.get_json()
        access_token = response["data"]["access_token"]

        # create dummy user here
        params = {
            "username"     : "jennie",
            "name"         : "jennie",
            "phone_ext"    : "62",
            "phone_number" : "81219643444",
            "email"        : "jennie@bp.com",
            "password"     : "password",
            "pin"          : "123456",
            "role"         : "USER"
        }
        result = self.create_user(params, access_token)
        response = result.get_json()

        user_id = response["data"]["user_id"]
        wallet_id = response["data"]["wallet_id"]

        va = VirtualAccount.query.filter_by(wallet_id=wallet_id).first()
        params = {
            "virtual_account"    : va.id,
            "trx_id"             : va.trx_id,
            "payment_amount"     : 50000,
            "payment_ntb"        : "119691111",
            "payment_channel_key": "BNI_VA", # BNI_VA CALLBACK
        }

        result = CallbackServices().deposit(params)
        self.assertEqual(result["status_code"], 0)

        transaction = Transaction.query.filter_by(wallet_id=wallet_id).first()

    def test_withdraw_success(self):
        """ test successfull withdraw """
        # get admin access token first
        result = self.get_access_token("MODANAADMIN", "password")
        response = result.get_json()
        access_token = response["data"]["access_token"]

        # create dummy user here
        params = {
            "username"     : "jennie",
            "name"         : "jennie",
            "phone_ext"    : "62",
            "phone_number" : "81219643444",
            "email"        : "jennie@bp.com",
            "password"     : "password",
            "pin"          : "123456",
            "role"         : "USER"
        }
        result = self.create_user(params, access_token)
        response = result.get_json()

        user_id = response["data"]["user_id"]
        wallet_id = response["data"]["wallet_id"]

        va = VirtualAccount.query.filter_by(wallet_id=wallet_id).first()
        params = {
            "virtual_account"    : va.id,
            "trx_id"             : va.trx_id,
            "payment_amount"     : 100000,
            "payment_ntb"        : "119691111",
            "payment_channel_key": "BNI_VA", # BNI_VA CALLBACK
        }

        result = CallbackServices().deposit(params)
        self.assertEqual(result["status_code"], 0)

        transaction = Transaction.query.filter_by(wallet_id=wallet_id).first()

        params = {
            "virtual_account"    : va.id,
            "trx_id"             : va.trx_id,
            "payment_amount"     : -50000,
            "payment_ntb"        : "119691111",
            "payment_channel_key": "BNI_VA", # BNI_VA CALLBACK
        }

        result = CallbackServices().withdraw(params)
        self.assertEqual(result["status_code"], 0)

    def test_withdraw_failed_insufficient_balance(self):
        """ test failed withdraw because of insufficient balance"""
        # get admin access token first
        result = self.get_access_token("MODANAADMIN", "password")
        response = result.get_json()
        access_token = response["data"]["access_token"]

        # create dummy user here
        params = {
            "username"     : "jennie",
            "name"         : "jennie",
            "phone_ext"    : "62",
            "phone_number" : "81219643444",
            "email"        : "jennie@bp.com",
            "password"     : "password",
            "pin"          : "123456",
            "role"         : "USER"
        }
        result = self.create_user(params, access_token)
        response = result.get_json()

        user_id   = response["data"]["user_id"]
        wallet_id = response["data"]["wallet_id"]

        va = VirtualAccount.query.filter_by(wallet_id=wallet_id).first()
        params = {
            "virtual_account"    : va.id,
            "trx_id"             : va.trx_id,
            "payment_amount"     : 100000,
            "payment_ntb"        : "119691111",
            "payment_channel_key": "BNI_VA", # BNI_VA CALLBACK
        }

        result = CallbackServices().deposit(params)
        self.assertEqual(result["status_code"], 0)

        transaction = Transaction.query.filter_by(wallet_id=wallet_id).first()

        params = {
            "virtual_account"    : va.id,
            "trx_id"             : va.trx_id,
            "payment_amount"     : -500000,
            "payment_ntb"        : "119691111",
            "payment_channel_key": "BNI_VA", # BNI_VA CALLBACK
        }

        result = CallbackServices().withdraw(params)
        self.assertEqual(result["status_code"], "400")

        transaction = Transaction.query.filter_by(wallet_id=wallet_id).all()
#end class
