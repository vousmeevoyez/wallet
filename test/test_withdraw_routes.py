import sys
import unittest
from unittest.mock import Mock, patch
import json

sys.path.append("../")
sys.path.append("../app")

# FLASK

from app         import create_app, db
from app.config  import config
from app.models  import User, Wallet


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

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

        self.mock_post_patcher.stop()

    """
        HELPER
    """

    def _request_withdraw(self, wallet_id, amount, pin):
        return self.client.post(
            '/withdraw/request',
            data=dict(
                wallet_id=wallet_id,
                pin=pin,
                amount=amount
            )
        )

    def _deposit(self, access_token, wallet_id, amount):
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.post(
            '/wallet/deposit',
            data=dict(
                wallet_id=wallet_id,
                amount=amount
            ),
            headers=headers
        )

    def _create_wallet(self, access_token, name, msisdn, pin, user_id):
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.post(
            '/wallet/create',
            data=dict(
                name=name,
                msisdn=msisdn,
                pin=pin,
                user_id=user_id,
            ),
            headers=headers
        )


    def _request_token(self, username, password):
        return self.client.post(
            '/auth/request_token',
                data=dict(
                    username=username,
                    password=password
            )
        )


    """
        WITHDRAW
    """
    def test_request_withdraw_success(self):
         # add user first
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            msisdn='081219644314',
        )
        user.set_password("password")
        db.session.add(user)

         # GET ACCESS TOKEN
        response = self._request_token("lisabp", "password")
        result = response.get_json()
        access_token = result["data"]["access_token"]

        # add user first
        user = User(
            username='admin',
            name='admin',
            email='admin@bp.com',
            msisdn='081209644314',
            role=1,
        )
        user.set_password("password")
        db.session.add(user)

         # GET ACCESS TOKEN
        response = self._request_token("admin", "password")
        result = response.get_json()
        access_token_admin = result["data"]["access_token"]

        # generate mock responses
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        # create actual wallet
        result = self._create_wallet(access_token, "rose", "081219644314", "123456", "1")
        response = result.get_json()

        wallet_id = response["data"]["wallet_id"]

        # deposit balance
        result = self._deposit(access_token_admin, wallet_id, "9999")
        response = result.get_json()

        result = self._request_withdraw(wallet_id, "9999", "123456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 0)

    def test_request_withdraw_failed_incorrect_pin(self):
         # add user first
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            msisdn='081219644314',
        )
        user.set_password("password")
        db.session.add(user)

         # GET ACCESS TOKEN
        response = self._request_token("lisabp", "password")
        result = response.get_json()
        access_token = result["data"]["access_token"]

        # add user first
        user = User(
            username='admin',
            name='admin',
            email='admin@bp.com',
            msisdn='081209644314',
            role=1,
        )
        user.set_password("password")
        db.session.add(user)

         # GET ACCESS TOKEN
        response = self._request_token("admin", "password")
        result = response.get_json()
        access_token_admin = result["data"]["access_token"]

        # generate mock responses
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        # create actual wallet
        result = self._create_wallet(access_token, "rose", "081219644314", "123456", "1")
        response = result.get_json()

        wallet_id = response["data"]["wallet_id"]

        # deposit balance
        result = self._deposit(access_token_admin, wallet_id, "9999")
        response = result.get_json()

        result = self._request_withdraw(wallet_id, "10000", "223456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)

    def test_request_withdraw_failed_insufficient_amount(self):
         # add user first
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            msisdn='081219644314',
        )
        user.set_password("password")
        db.session.add(user)

         # GET ACCESS TOKEN
        response = self._request_token("lisabp", "password")
        result = response.get_json()
        access_token = result["data"]["access_token"]

        # add user first
        user = User(
            username='admin',
            name='admin',
            email='admin@bp.com',
            msisdn='081209644314',
            role=1,
        )
        user.set_password("password")
        db.session.add(user)

         # GET ACCESS TOKEN
        response = self._request_token("admin", "password")
        result = response.get_json()
        access_token_admin = result["data"]["access_token"]

        # generate mock responses
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        # create actual wallet
        result = self._create_wallet(access_token, "rose", "081219644314", "123456", "1")
        response = result.get_json()

        wallet_id = response["data"]["wallet_id"]

        # deposit balance
        result = self._deposit(access_token_admin, wallet_id, "9999")
        response = result.get_json()

        result = self._request_withdraw(wallet_id, "10000", "123456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)

    def test_request_withdraw_failed_max_amount_exceed(self):
         # add user first
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            msisdn='081219644314',
        )
        user.set_password("password")
        db.session.add(user)

         # GET ACCESS TOKEN
        response = self._request_token("lisabp", "password")
        result = response.get_json()
        access_token = result["data"]["access_token"]

        # add user first
        user = User(
            username='admin',
            name='admin',
            email='admin@bp.com',
            msisdn='081209644314',
            role=1,
        )
        user.set_password("password")
        db.session.add(user)

         # GET ACCESS TOKEN
        response = self._request_token("admin", "password")
        result = response.get_json()
        access_token_admin = result["data"]["access_token"]

        # generate mock responses
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        # create actual wallet
        result = self._create_wallet(access_token, "rose", "081219644314", "123456", "1")
        response = result.get_json()

        wallet_id = response["data"]["wallet_id"]

        # deposit balance
        result = self._deposit(access_token_admin, wallet_id, "9999")
        response = result.get_json()

        result = self._request_withdraw(wallet_id, "99999999999", "123456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)

    def test_request_withdraw_failed_less_minimal_amount(self):
         # add user first
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            msisdn='081219644314',
        )
        user.set_password("password")
        db.session.add(user)

         # GET ACCESS TOKEN
        response = self._request_token("lisabp", "password")
        result = response.get_json()
        access_token = result["data"]["access_token"]

        # add user first
        user = User(
            username='admin',
            name='admin',
            email='admin@bp.com',
            msisdn='081209644314',
            role=1,
        )
        user.set_password("password")
        db.session.add(user)

         # GET ACCESS TOKEN
        response = self._request_token("admin", "password")
        result = response.get_json()
        access_token_admin = result["data"]["access_token"]

        # generate mock responses
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        # create actual wallet
        result = self._create_wallet(access_token, "rose", "081219644314", "123456", "1")
        response = result.get_json()

        wallet_id = response["data"]["wallet_id"]

        # deposit balance
        result = self._deposit(access_token_admin, wallet_id, "9999")
        response = result.get_json()

        result = self._request_withdraw(wallet_id, "1", "123456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)

    def test_request_withdraw_failed_wallet_not_found(self):
         # add user first
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            msisdn='081219644314',
        )
        user.set_password("password")
        db.session.add(user)

         # GET ACCESS TOKEN
        response = self._request_token("lisabp", "password")
        result = response.get_json()
        access_token = result["data"]["access_token"]

        # add user first
        user = User(
            username='admin',
            name='admin',
            email='admin@bp.com',
            msisdn='081209644314',
            role=1,
        )
        user.set_password("password")
        db.session.add(user)

         # GET ACCESS TOKEN
        response = self._request_token("admin", "password")
        result = response.get_json()
        access_token_admin = result["data"]["access_token"]

        # generate mock responses
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        # create actual wallet
        result = self._create_wallet(access_token, "rose", "081219644314", "123456", "1")
        response = result.get_json()

        wallet_id = response["data"]["wallet_id"]

        # deposit balance
        result = self._deposit(access_token_admin, wallet_id, "9999")
        response = result.get_json()

        result = self._request_withdraw("1231", "1", "123456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 404)

    def test_request_withdraw_failed_bni_error(self):
         # add user first
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            msisdn='081219644314',
        )
        user.set_password("password")
        db.session.add(user)

         # GET ACCESS TOKEN
        response = self._request_token("lisabp", "password")
        result = response.get_json()
        access_token = result["data"]["access_token"]

        # add user first
        user = User(
            username='admin',
            name='admin',
            email='admin@bp.com',
            msisdn='081209644314',
            role=1,
        )
        user.set_password("password")
        db.session.add(user)

         # GET ACCESS TOKEN
        response = self._request_token("admin", "password")
        result = response.get_json()
        access_token_admin = result["data"]["access_token"]

        # generate mock responses
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        # create actual wallet
        result = self._create_wallet(access_token, "rose", "081219644314", "123456", "1")
        response = result.get_json()

        wallet_id = response["data"]["wallet_id"]

        # deposit balance
        result = self._deposit(access_token_admin, wallet_id, "999999")
        response = result.get_json()

        expected_value = {
            "status"  : "002",
            "message" : "IP address not allowed or wrong Client ID."
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        result = self._request_withdraw(wallet_id, "10000", "123456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)

if __name__ == "__main__":
    unittest.main(verbosity=2)
