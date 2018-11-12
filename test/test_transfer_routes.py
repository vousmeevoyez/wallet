import sys
import unittest
import json

from unittest.mock import Mock, patch

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

class TestTransferRoutes(unittest.TestCase):

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

    def _deposit(self, wallet_id, amount):
        return self.client.post(
            '/wallet/deposit',
            data=dict(
                wallet_id=wallet_id,
                amount=amount
            )
        )

    def _direct_transfer(self, source, destination, amount, notes, pin):
        return self.client.post(
            '/transfer/direct',
            data=dict(
                source=source,
                destination=destination,
                amount=amount,
                notes=notes,
                pin=pin
            )
        )

    def _bulk_transfer(self, source, transaction_list, pin):
        return self.client.post(
            '/transfer/bulk',
            data=dict(
                source=source,
                transaction_list=transaction_list,
                pin=pin
            )
        )


    """
        TRANFSER
    """

    def test_direct_transfer_success(self):
        # generate account
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        result = self._register_user("jennie", "Jennie", "081219644324", "jennie@blackpink.com", "password", "123456", "2")
        response = result.get_json()
        print(response)
        source = response["data"]["wallet_id"]

        # generate account
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "124", 'virtual_account': "112222" }
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        result = self._register_user("rose", "Rose", "081219644323", "rose@blackpink.com", "password", "123456", "2")
        response = result.get_json()
        print(response)


if __name__ == "__main__":
    unittest.main(verbosity=2)
