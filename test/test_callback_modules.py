import sys
import unittest
from unittest.mock import Mock, patch
import json

sys.path.append("../")
sys.path.append("../app")

# FLASK

from app                  import create_app, db
from app.config           import config
from app.models           import User, VirtualAccount, Wallet
from app.callback.modules import callback

class TestConfig(config.Config):

    TESTING = True
    #SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SQLALCHEMY_DATABASE_URI = 'postgresql://modana:password@localhost/unittest_db'

class TestCallbackModules(unittest.TestCase):

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
    #end def

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
        CALLBACK MODULES
    """
    def test_deposit_success(self):
        data = {
            "virtual_account": self.va.id,
            "customer_name"  : self.va.name,
            "trx_id"         : self.va.trx_id,
            "payment_amount" : 50000,
        }
        response = callback.CallbackController().deposit( data )

        self.assertEqual(response["status"], "000")

        # make sure balance is injected
        wallet = Wallet.query.filter_by(id=self.wallet_id).first()
        self.assertEqual(wallet.balance, data["payment_amount"])
    #end def

    def test_deposit_failed_va_not_found(self):
        data = {
            "virtual_account": "123",
            "customer_name"  : self.va.name,
            "trx_id"         : self.va.trx_id,
            "payment_amount" : 99,
        }
        response = callback.CallbackController().deposit( data )

        self.assertEqual(response["status"], "404")
    #end def

    def test_inject_success(self):
        data = {
            "id"     : self.wallet_id,
            "amount" : 99,
        }
        response = callback.CallbackController()._inject( data )

        self.assertEqual(response["status"], "SUCCESS")

        # make sure balance is injected
        wallet = Wallet.query.filter_by(id=self.wallet_id).first()
        self.assertEqual(wallet.balance, data["amount"])
    #end def

if __name__ == "__main__":
    unittest.main(verbosity=2)
