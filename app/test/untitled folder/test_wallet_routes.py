import sys
import unittest
from unittest.mock import Mock, patch
import json

sys.path.append("../")
sys.path.append("../app")

# FLASK

from app         import create_app, db
from app.config  import config
from app.models  import User, Wallet, VirtualAccount, Transaction
from app.serializer import WalletSchema


class TestConfig(config.Config):

    TESTING = True
    #SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SQLALCHEMY_DATABASE_URI = 'postgresql://modana:password@localhost/unittest_db'

class TestWalletRoutes(unittest.TestCase):

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

    def _init_test(self):
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
        self.access_token = result["data"]["access_token"]

    """
        HELPER
    """

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

    def _get_wallet_list(self, access_token, id):
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.get(
            '/wallet/list?id=' + id,
            headers=headers
        )

    def _get_wallet_details(self, access_token, wallet_id, pin):
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.post(
            '/wallet/info',
            data=dict(
                wallet_id=wallet_id,
                pin=pin
            ),
            headers=headers
        )

    def _remove_wallet(self, access_token, wallet_id, pin):
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.delete(
            '/wallet/info',
            data=dict(
                wallet_id=wallet_id,
                pin=pin,
            ),
            headers=headers
        )

    def _check_balance(self, access_token, wallet_id, pin):
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.post(
            '/wallet/balance',
            data=dict(
                wallet_id=wallet_id,
                pin=pin
            ),
            headers=headers
        )

    def _lock(self, access_token, wallet_id):
        return self.client.get(
            '/wallet/lock?id=' + wallet_id,
            headers=headers
        )

    def _unlock(self, access_token, wallet_id):
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.get(
            '/wallet/unlock?id=' + wallet_id,
            headers=headers
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

    def _transaction_history(self, access_token, wallet_id):
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.get(
            '/wallet/transaction_history?id=' + wallet_id,
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
        WALLET
    """
    def test_create_wallet_success(self):
        # generate mock responses
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        # create actual wallet
        result = self._create_wallet(self.access_token, "rose", "081219644314", "123456", "1")
        response = result.get_json()

        # MAKE SURE WALLET SUCCESSFULLY CREATED AND LINKED TO USER
        user = User.query.get(1)
        self.assertEqual(len(user.wallets), 1)

    def test_create_wallet_empty_error(self):
        result = self._create_wallet(self.access_token, "", "", "", "")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)

    def test_create_wallet_failed(self):
        # generate mock up responses
        expected_value = {
            "status" : "009",
            "message" : "Unexpected Error"
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        #create actual wallet
        result = self._create_wallet(self.access_token, "rose", "081219644314", "123456", "1")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)
        self.assertEqual(response["data"], "Virtual Account Creation Failed")

    def test_wallet_list(self):
        # generate mock responses
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        # create actual wallet
        result = self._create_wallet(self.access_token, "rose", "081219644314", "123456", "1")
        response = result.get_json()

        # generate mock responses
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        # create actual wallet
        result = self._create_wallet(self.access_token, "rose", "081219644314", "123456", "1")
        response = result.get_json()

        #create actual wallet
        result = self._create_wallet(self.access_token, "rose", "081219644314", "123456", "1")
        response = result.get_json()

        result = self._get_wallet_list(self.access_token, "1")
        response = result.get_json()

        # CHECK WALLET IN DATABASES
        wallet = Wallet.query.filter_by(user_id=1)
        test = WalletSchema(many=True).dump(wallet).data

        self.assertEqual(response["status_code"], 0)
        self.assertEqual(len(response["data"]), len(test))

    def test_transaction_history(self):
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
        result = self._create_wallet(self.access_token, "rose", "081219644314", "123456", "1")
        response = result.get_json()

        wallet_id = response["data"]["wallet_id"]

        # checking transaction history
        result = self._transaction_history(self.access_token, wallet_id)
        response = result.get_json()

        self.assertEqual(response["status_code"], 0)
        self.assertEqual(len(response["data"]), 0)

    def test_wallet_details_success(self):
        # generate mock response
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        # create actual wallet
        result = self._create_wallet(self.access_token, "rose", "081219644314", "123456", "1")
        response = result.get_json()

        wallet_id = response["data"]["wallet_id"]

        # CHECK WALLET DETAILS
        result = self._get_wallet_details(self.access_token, wallet_id, "123456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 0)

    def test_wallet_details_failed(self):
        result = self._get_wallet_details(self.access_token, "12345", "223456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)

    def test_wallet_details_incorrect_pin(self):
        # generate mock response
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        # create actual wallet
        result = self._create_wallet(self.access_token, "rose", "081219644314", "123456", "1")
        response = result.get_json()

        wallet_id = response["data"]["wallet_id"]

        # CHECK WALLET DETAILS
        result = self._get_wallet_details(self.access_token, wallet_id, "122456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)

    def test_wallet_remove(self):
        # generate mock response
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        # create actual wallet
        result = self._create_wallet(self.access_token, "rose", "081219644314", "123456", "1")
        response = result.get_json()

        # create actual wallet
        result = self._create_wallet(self.access_token, "rose", "081219644314", "123456", "1")
        response = result.get_json()

        wallet_id = response["data"]["wallet_id"]

        result = self._remove_wallet(self.access_token, wallet_id, "123456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 0)

        result = self._get_wallet_list(self.access_token, "1")
        response = result.get_json()

        self.assertEqual(len(response["data"]), 1)

    def test_wallet_remove_failed(self):
        # generate mock response
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        # create actual wallet
        result = self._create_wallet(self.access_token, "rose", "081219644314", "123456", "1")
        response = result.get_json()

        wallet_id = response["data"]["wallet_id"]

        result = self._remove_wallet(self.access_token, wallet_id, "123456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)

    def test_wallet_remove_failed_not_found(self):
        # GENERATE WALLET FIRST
        result = self._remove_wallet(self.access_token, "123", "123456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)

    def test_check_wallet_balance_success(self):
        # generate mock response
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        # create actual wallet
        result = self._create_wallet(self.access_token, "rose", "081219644314", "123456", "1")
        response = result.get_json()

        wallet_id = response["data"]["wallet_id"]

        result = self._check_balance(self.access_token, wallet_id, "123456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 0)
        self.assertEqual(response["data"]["balance"], 0)

    def test_check_wallet_balance_failed(self):
        # generate mock response
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        # create actual wallet
        result = self._create_wallet(self.access_token, "rose", "081219644314", "123456", "1")
        response = result.get_json()

        wallet_id = response["data"]["wallet_id"]

        result = self._check_balance(self.access_token, "123213", "213456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)

if __name__ == "__main__":
    unittest.main(verbosity=2)
