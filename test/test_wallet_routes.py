import sys
import unittest
from unittest.mock import Mock, patch
import json

sys.path.append("../")
sys.path.append("../app")

# FLASK

from app         import create_app, db
from app.config  import config
from app.models  import ApiKey, Wallet
from app.bank    import handler


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

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

        self.mock_post_patcher.stop()

    """
        HELPER
    """

    def _create_wallet(self, name, msisdn, email, pin):
        return self.client.post(
            '/wallet/create',
            data=dict(
                name=name,
                msisdn=msisdn,
                email=email,
                pin=pin,
            )
        )

    def _get_wallet_list(self):
        return self.client.get(
            '/wallet/list',
        )

    def _get_wallet_details(self, wallet_id, pin):
        return self.client.post(
            '/wallet/get_info',
            data=dict(
                id=wallet_id,
                pin=pin
            )
        )

    def _remove_wallet(self, wallet_id):
        return self.client.get(
            '/wallet/remove?id=' + wallet_id,
        )

    def _check_balance(self, wallet_id, pin):
        return self.client.post(
            '/wallet/check_balance',
            data=dict(
                id=wallet_id,
                pin=pin
            )
        )

    def _lock(self, wallet_id):
        return self.client.get(
            '/wallet/lock?id=' + wallet_id,
        )

    def _unlock(self, wallet_id):
        return self.client.get(
            '/wallet/unlock?id=' + wallet_id,
        )

    def _deposit(self, wallet_id):
        return self.client.get(
            '/wallet/deposit?id=' + wallet_id,
        )

    def _transaction_history(self, wallet_id):
        return self.client.get(
            '/wallet/transaction_history?id=' + wallet_id,
        )

    """
        WALLET
    """
    def test_create_wallet_success(self):
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        # MOCK RESPONSE
        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        result = self._create_wallet("rose", "081219644314", "rose@blackpink.com", "123456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 0)
        self.assertTrue(response["data"]["wallet_id"])

    def test_create_wallet_duplicate(self):
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        # MOCK RESPONSE
        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        result = self._create_wallet("rose", "081219644314", "rose@blackpink.com", "123456")
        response = result.get_json()

        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        # MOCK RESPONSE
        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        result = self._create_wallet("rose", "081219644314", "rose@blackpink.com", "123456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)

    def test_create_wallet_empty_error(self):
        result = self._create_wallet("", "", "", "")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)

    def test_create_wallet_failed(self):
        expected_value = {
            "status" : "009",
            "message" : "Unexpected Error"
        }

        # MOCK RESPONSE
        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        result = self._create_wallet("rose", "081219644314", "rose@blackpink.com", "123456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)
        self.assertEqual(response["data"], "Virtual Account Creation Failed")

    def test_wallet_list(self):
        self._create_wallet("rose", "081219644314", "rose@blackpink.com", "123456")

        result = self._get_wallet_list()
        response = result.get_json()

        self.assertEqual(response["status_code"], 0)
        self.assertEqual(len(response["data"]), 1)

    def test_wallet_details_success(self):
        # GENERATE WALLET FIRST
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        # MOCK RESPONSE
        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        result = self._create_wallet("rose", "081219644314", "rose@blackpink.com", "123456")
        response = result.get_json()
        wallet_id = response["data"]["wallet_id"]

        # CHECK WALLET DETAILS
        result = self._get_wallet_details(wallet_id, "123456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 0)

    def test_wallet_details_failed(self):
        result = self._get_wallet_details("12345", "223456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 404)

    def test_wallet_details_incorrect_pin(self):
        # GENERATE WALLET FIRST
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        # MOCK RESPONSE
        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        result = self._create_wallet("rose", "081219644314", "rose@blackpink.com", "123456")
        response = result.get_json()
        wallet_id = response["data"]["wallet_id"]

        # CHECK WALLET DETAILS
        result = self._get_wallet_details(wallet_id, "124456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)

    def test_wallet_remove(self):
        # GENERATE WALLET FIRST
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        # MOCK RESPONSE
        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        result = self._create_wallet("rose", "081219644314", "rose@blackpink.com", "123456")
        response = result.get_json()
        wallet_id = response["data"]["wallet_id"]

        result = self._remove_wallet(wallet_id)
        response = result.get_json()

        self.assertEqual(response["status_code"], 0)

        result = self._get_wallet_list()
        response = result.get_json()

        self.assertEqual(len(response["data"]), 0)

    def test_wallet_remove_failed(self):
        # GENERATE WALLET FIRST
        result = self._remove_wallet("123")
        response = result.get_json()

        self.assertEqual(response["status_code"], 404)

    def test_check_wallet_balance_success(self):
        # GENERATE WALLET FIRST
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        # MOCK RESPONSE
        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        result = self._create_wallet("rose", "081219644314", "rose@blackpink.com", "123456")
        response = result.get_json()
        wallet_id = response["data"]["wallet_id"]

        result = self._check_balance(wallet_id, "123456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 0)
        self.assertEqual(response["data"]["balance"], 0)

    def test_check_wallet_balance_failed(self):
        # GENERATE WALLET FIRST
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        # MOCK RESPONSE
        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        result = self._create_wallet("rose", "081219644314", "rose@blackpink.com", "123456")
        response = result.get_json()
        wallet_id = response["data"]["wallet_id"]

        result = self._check_balance(wallet_id, "213456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)

        result = self._check_balance("123213", "213456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 404)

    def test_lock_wallet(self):
        # GENERATE WALLET FIRST
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        # MOCK RESPONSE
        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        result = self._create_wallet("rose", "081219644314", "rose@blackpink.com", "123456")
        response = result.get_json()
        wallet_id = response["data"]["wallet_id"]

        result = self._lock(wallet_id)
        response = result.get_json()

        self.assertEqual(response["status_code"], 0)

        result = self._lock("1234")
        response = result.get_json()

        self.assertEqual(response["status_code"], 404)

        result = self._lock(wallet_id)
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)

    def test_unlock_wallet(self):
        # GENERATE WALLET FIRST
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        # MOCK RESPONSE
        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        result = self._create_wallet("rose", "081219644314", "rose@blackpink.com", "123456")
        response = result.get_json()
        wallet_id = response["data"]["wallet_id"]

        result = self._unlock(wallet_id)
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)

        result = self._unlock("1232")
        response = result.get_json()

        self.assertEqual(response["status_code"], 404)

    def test_wallet_mutation(self):
        # GENERATE WALLET FIRST
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        # MOCK RESPONSE
        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        result = self._create_wallet("rose", "081219644314", "rose@blackpink.com", "123456")
        response = result.get_json()
        wallet_id = response["data"]["wallet_id"]

        result = self._transaction_history(wallet_id)
        response = result.get_json()

        self.assertEqual(response["status_code"], 0)
        self.assertEqual(len(response["data"]), 0)

    def test_wallet_mutation_failed(self):
        result = self._transaction_history("0235")
        response = result.get_json()

        self.assertEqual(response["status_code"], 404)

if __name__ == "__main__":
    unittest.main(verbosity=2)
