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

    def _request_withdraw(self, wallet_id, pin):
        return self.client.post(
            '/withdraw/request',
            data=dict(
                wallet_id=wallet_id,
                pin=pin,
            )
        )

    """
        WITHDRAW
    """
    def test_request_withdraw(self):
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        # MOCK RESPONSE
        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        result = self._request_withdraw("rose", "081219644314", "rose@blackpink.com", "123456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 0)
        self.assertTrue(response["data"]["wallet_id"])

if __name__ == "__main__":
    unittest.main(verbosity=2)
