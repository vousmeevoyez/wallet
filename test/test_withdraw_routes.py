import sys
import unittest
import uuid
import random
from unittest.mock import Mock, patch
import json

sys.path.append("../")
sys.path.append("../app")

# FLASK

from app         import create_app, db
from app.config  import config
from app.models  import User, Wallet, VirtualAccount
from app.bank.utility   import remote_call

BNI_ECOLLECTION_CONFIG = config.Config.BNI_ECOLLECTION_CONFIG


class TestConfig(config.Config):

    TESTING = True
    #SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SQLALCHEMY_DATABASE_URI = 'postgresql://modana:password@localhost/unittest_db'

class TestWithdrawRoutes(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.client = self.app.test_client()

        self.mock_post_patcher = patch("app.bank.utility.remote_call.requests.post")
        self.mock_post = self.mock_post_patcher.start()

        self._init_test()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

        self.mock_post_patcher.stop()

    def _generate_random_id(self, string_length=10):
        random = str(uuid.uuid4())
        random = random.upper()
        random = random.replace("-", "")
        return random[0:string_length]

    def _generate_first_part(self):
        first_digit = random.randint(10,99)
        return first_digit

    def _generate_second_part(self):
        middle = 0
        while middle == 0:
            middle1 = random.randint(0,9)
            middle2 = random.randint(0,9)
            middle3 = random.randint(0,9)
            middle  = 100 * middle1 + 10 * middle2 + middle3
        return middle

    def _generate_third_part(self):
        return ''.join(map(str,random.sample(range(10),4)))

    def _generate_msisdn(self):
        fixed  = '081'
        first  = self._generate_first_part()
        second = self._generate_second_part()
        third  = self._generate_third_part()
        return fixed + '{}{}{}'.format(first,second,third)

    def _init_test(self):
        # create dummy user account
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        # MOCK RESPONSE
        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        user_id = self._generate_random_id()
        msisdn  = self._generate_msisdn()
        email   = user_id + "@test.com"

        result = self._register_user(user_id, user_id, msisdn, email, "password", "123456", "2")
        response = result.get_json()

        # make sure user successfully created
        self.assertEqual(response["status_code"], 0)
        self.assertTrue(response["data"]["wallet_id"])

        self.wallet_id = response["data"]["wallet_id"]
        # fetch VA object
        self.va = VirtualAccount.query.filter_by(wallet_id=self.wallet_id).first()

        # GET ACCESS TOKEN
        response = self._request_token(user_id, "password")
        result = response.get_json()
        self.access_token = result["data"]["access_token"]

        # MOCK CALLBACK TO INJECT BALANCE
        data = {
            "virtual_account"           : str(self.va.id),
            "customer_name"             : str(self.va.name),
            "trx_id"                    : str(self.va.trx_id),
            "trx_amount"                : str(self.va.trx_amount),
            "payment_amount"            : "500000",
            "cumulative_payment_amount" : "500000",
            "payment_ntb"               : "12345",
            "datetime_payment"          : "2018-11-24 14:00:00",
        }
        encrypted_data = remote_call.encrypt(BNI_ECOLLECTION_CONFIG["CREDIT_CLIENT_ID"], BNI_ECOLLECTION_CONFIG["CREDIT_SECRET_KEY"], data)

        expected_value = {
            "client_id" : BNI_ECOLLECTION_CONFIG["CREDIT_CLIENT_ID"],
            "data"      : encrypted_data.decode("UTF-8")
        }

        result = self._callback_deposit(expected_value)
        response = result.get_json()

        self.assertEqual( response["status"], "000")

    """
        HELPER
    """
    def _register_user(self, username, name, msisdn, email, password, pin, role):
        return self.client.post(
            '/user/register',
            data=dict(
                username=username,
                name=name,
                msisdn=msisdn,
                email=email,
                password=password,
                pin=pin,
                role=role
            )
        )

    def _request_withdraw(self, wallet_id, amount, pin):
        return self.client.post(
            '/withdraw/request',
            data=dict(
                wallet_id=wallet_id,
                pin=pin,
                amount=amount
            )
        )

    def _request_token(self, username, password):
        return self.client.post(
            '/auth/request_token',
                data=dict(
                    username=username,
                    password=password
            )
        )

    def _callback_deposit(self, json):
        return self.client.post(
            '/callback/deposit',
            json=json
        )


    """
        WITHDRAW
    """
    def test_request_withdraw_success(self):
        result = self._request_withdraw(self.wallet_id, "50000", "123456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 0)

        # make sure there are now 2 VA
        va = VirtualAccount.query.filter_by(wallet_id=self.wallet_id).all()
        self.assertEqual(len(va), 2)

    def test_request_withdraw_failed_incorrect_pin(self):
        result = self._request_withdraw(self.wallet_id, "10000", "223456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)

        # make sure no va is created when va failed
        va = VirtualAccount.query.filter_by(wallet_id=self.wallet_id).all()
        self.assertEqual(len(va), 1)

    def test_request_withdraw_failed_insufficient_amount(self):
        result = self._request_withdraw(self.wallet_id, "10000", "123456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)

        # make sure no va is created when va failed
        va = VirtualAccount.query.filter_by(wallet_id=self.wallet_id).all()
        self.assertEqual(len(va), 1)

    def test_request_withdraw_failed_max_amount_exceed(self):
        result = self._request_withdraw(self.wallet_id, "99999999999", "123456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)

        # make sure no va is created when va failed
        va = VirtualAccount.query.filter_by(wallet_id=self.wallet_id).all()
        self.assertEqual(len(va), 1)

    def test_request_withdraw_failed_less_minimal_amount(self):
        result = self._request_withdraw(self.wallet_id, "1", "123456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)

        # make sure no va is created when va failed
        va = VirtualAccount.query.filter_by(wallet_id=self.wallet_id).all()
        self.assertEqual(len(va), 1)

    def test_request_withdraw_failed_wallet_not_found(self):
        result = self._request_withdraw("1231", "1", "123456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 404)

        # make sure no va is created when va failed
        va = VirtualAccount.query.filter_by(wallet_id=self.wallet_id).all()
        self.assertEqual(len(va), 1)

    def test_request_withdraw_failed_bni_error(self):
        expected_value = {
            "status"  : "002",
            "message" : "IP address not allowed or wrong Client ID."
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value = expected_value

        result = self._request_withdraw(self.wallet_id, "10000", "123456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)

        # make sure no va is created when va failed
        va = VirtualAccount.query.filter_by(wallet_id=self.wallet_id).all()
        self.assertEqual(len(va), 1)

if __name__ == "__main__":
    unittest.main(verbosity=2)
