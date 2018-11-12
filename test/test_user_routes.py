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

    def _user_list(self, page):
        return self.client.get(
            '/user/list?page=' + page,
        )

    def _user_info(self, id):
        return self.client.get(
            '/user/info/' + id,
        )

    def _user_remove(self, id):
        return self.client.delete(
            '/user/info/' + id,
        )
    def _user_update(self, id, name, msisdn, email):
        return self.client.put(
            '/user/info/' + id,
            data=dict(
                name=name,
                msisdn=msisdn,
                email=email,
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

        result = self._register_user("kevlin", "sada", "081219644324", "rrara@blackpink.com", "password", "123456", "1")
        response = result.get_json()

        self.assertEqual(response["status_code"], 0)
        self.assertTrue(response["data"]["wallet_id"])

        # check database entry make sure data inserted correctly
        user = User.query.all()
        self.assertEqual(len(user), 1)

        wallet = Wallet.query.all()
        self.assertEqual(len(wallet), 1)

        va = VirtualAccount.query.all()
        self.assertEqual(len(va), 1)

    """
    def test_register_user_duplicate_failed(self):
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        # MOCK RESPONSE
        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        result = self._register_user("kevlin", "sada", "081219644324", "rrara@blackpink.com", "password", "123456", "1")
        response = result.get_json()

        self.assertEqual(response["status_code"], 0)
        self.assertTrue(response["data"]["wallet_id"])

        # DUPLICATE ENTRY ERROR
        result = self._register_user("kevlin", "sada", "081219644324", "rrara@blackpink.com", "password", "123456", "1")
        response = result.get_json()
        print(response)

        self.assertEqual(response["status_code"], 400)
    """

    def test_register_user_va_failed(self):
        result = self._register_user("kevlin", "sada", "081219644324", "rrara@blackpink.com", "password", "123456", "1")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)

        # check database entry make sure data inserted correctly
        user= User.query.all()
        self.assertEqual(len(user), 0)

        wallet = Wallet.query.all()
        self.assertEqual(len(wallet), 0)

        va = VirtualAccount.query.all()
        self.assertEqual(len(va), 0)

    def test_user_list(self):
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        # MOCK RESPONSE
        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        result = self._register_user("kevlin", "sada", "081219644324", "rrara@blackpink.com", "password", "123456", "1")
        result = self._user_list("1")
        response = result.get_json()

        self.assertEqual(response["status_code"], 0)
        self.assertEqual(len(response["data"]), 1)

    def test_user_info(self):
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        # MOCK RESPONSE
        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        result = self._register_user("kevlin", "sada", "081219644324", "rrara@blackpink.com", "password", "123456", "1")
        result = self._user_info("1")
        response = result.get_json()

        self.assertEqual(response["status_code"], 0)
        self.assertEqual(len(response["data"]), 2)

    def test_remove_user(self):
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        # MOCK RESPONSE
        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value
        result = self._register_user("kevlin", "sada", "081219644324", "rrara@blackpink.com", "password", "123456", "1")
        result = self._user_remove("1")
        response = result.get_json()

        self.assertEqual(response["status_code"], 0)

        # check database entry make sure data removed correctly
        user = User.query.all()
        self.assertEqual(len(user), 0)

        wallet = Wallet.query.all()
        self.assertEqual(len(wallet), 0)

        va = VirtualAccount.query.all()
        self.assertEqual(len(va), 0)

    def test_update_user(self):
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        # MOCK RESPONSE
        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value
        result = self._register_user("kevlin", "sada", "081219644324", "rrara@blackpink.com", "password", "123456", "1")
        result = self._user_update("1", "jennie", "081209644324", "jennie@blackpink.com")
        response = result.get_json()

        self.assertEqual(response["status_code"], 0)

        # make sure the record is updated
        user = User.query.get(1)
        self.assertEqual(user.name, "jennie")
        self.assertEqual(user.msisdn, "081209644324")
        self.assertEqual(user.email, "jennie@blackpink.com")

if __name__ == "__main__":
    unittest.main(verbosity=2)
