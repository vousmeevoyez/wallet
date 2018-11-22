import sys
import unittest
from unittest.mock import Mock, patch
import json

sys.path.append("../")
sys.path.append("../app")

# FLASK

from app         import create_app, db
from app.config  import config
from app.models  import User, Wallet, VirtualAccount


class TestConfig(config.Config):

    TESTING = True
    #SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SQLALCHEMY_DATABASE_URI = 'postgresql://modana:password@localhost/unittest_db'

class TestCallbackRoutes(unittest.TestCase):

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
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        # MOCK RESPONSE
        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        result = self._register_user("rose", "rosebp", "082219644324", "rose@blackpink.com", "password", "123456", "1")
        response = result.get_json()

        self.wallet_id = response["data"]["wallet_id"]

        self.va = VirtualAccount.query.filter_by(wallet_id=self.wallet_id).first()

    """
        HELPER
    """

    def _callback_deposit(self, va, name, trx_id, trx_amount, payment_amount, cumulative_amount, ref_number, datetime_payment):
        return self.client.post(
            '/callback/deposit',
            data=dict(
                virtual_account=va,
                customer_name=name,
                trx_id=trx_id,
                trx_amount=trx_amount,
                payment_amount=payment_amount,
                cumulative_payment_amount=cumulative_amount,
                payment_ntb=ref_number,
                datetime_payment=datetime_payment,
            ),
        )

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
        CALLBACK
    """
    def test_callback_deposit(self):
        result = self._callback_deposit( self.va.id, self.va.name, self.va.trx_id, self.va.trx_amount, "50000", "50000", "212", "2018-11-22 18:00:00")
        response = result.get_json()

        self.assertEqual( response["status_code"], 0)

        # make sure balance injected successfully
        wallet = Wallet.query.filter_by(id=self.wallet_id).first()
        self.assertEqual( wallet.balance, 50000)

if __name__ == "__main__":
    unittest.main(verbosity=2)
