import sys
import unittest
from unittest.mock import Mock, patch
import json

sys.path.append("../")
sys.path.append("../app")

# FLASK

from app         import create_app, db
from app.config  import config
from app.models  import User, VirtualAccount, Wallet
from app.bank    import helper


class TestConfig(config.Config):

    TESTING = True
    #SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SQLALCHEMY_DATABASE_URI = 'postgresql://modana:password@localhost/unittest_db'

class TestUserRoutes(unittest.TestCase):

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

    """
        USER
    """
    def test_register_user_success(self):
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        # MOCK RESPONSE
        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        result = self._register_user("kevlin", "sada", "081219644324", "rrara@blackpink.com", "password", "123456", "USER")
        response = result.get_json()

        self.assertEqual(response["status_code"], 0)
        self.assertTrue(response["data"]["wallet_id"])

    def test_register_user_duplicate_failed(self):
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        # MOCK RESPONSE
        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        result = self._register_user("kevlin", "sada", "081219644324", "rrara@blackpink.com", "password", "123456", "USER")
        response = result.get_json()

        self.assertEqual(response["status_code"], 0)
        self.assertTrue(response["data"]["wallet_id"])

        # DUPLICATE ENTRY ERROR
        result = self._register_user("kevlin", "sada", "081219644324", "rrara@blackpink.com", "password", "123456", "USER")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)

    def test_register_user_va_failed(self):
        result = self._register_user("kevlin", "sada", "081219644324", "rrara@blackpink.com", "password", "123456", "USER")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)

        # check database entry make sure no data inserted when record failed
        user = User.query.get(1)
        print(user)

        wallet = Wallet.query.all()
        print(wallet)

        va = VirtualAccount.query.all()
        print(va)

if __name__ == "__main__":
    unittest.main(verbosity=2)
