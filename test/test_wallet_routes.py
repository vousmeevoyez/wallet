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

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

        self.mock_post_patcher.stop()

    """
        HELPER
    """

    def _create_wallet(self, name, msisdn, pin, user_id):
        return self.client.post(
            '/wallet/create',
            data=dict(
                name=name,
                msisdn=msisdn,
                pin=pin,
                user_id=user_id,
            )
        )

    def _get_wallet_list(self, id):
        return self.client.get(
            '/wallet/list?id=' + id,
        )

    def _get_wallet_details(self, wallet_id, pin):
        return self.client.post(
            '/wallet/info',
            data=dict(
                wallet_id=wallet_id,
                pin=pin
            )
        )

    def _remove_wallet(self, wallet_id, pin):
        return self.client.delete(
            '/wallet/info',
            data=dict(
                wallet_id=wallet_id,
                pin=pin,
            )
        )

    def _check_balance(self, wallet_id, pin):
        return self.client.post(
            '/wallet/balance',
            data=dict(
                wallet_id=wallet_id,
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

    def _deposit(self, wallet_id, amount):
        return self.client.post(
            '/wallet/deposit',
            data=dict(
                wallet_id=wallet_id,
                amount=amount
            )
        )

    def _transaction_history(self, wallet_id):
        return self.client.get(
            '/wallet/transaction_history?id=' + wallet_id,
        )

    """
        WALLET
    """
    def test_create_wallet_success(self):
        # add user first
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            msisdn='081219644314',
        )
        user.set_password("password")
        db.session.add(user)

        # generate mock responses
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        # create actual wallet
        result = self._create_wallet("rose", "081219644314", "123456", "1")
        response = result.get_json()

        # MAKE SURE WALLET SUCCESSFULLY CREATED AND LINKED TO USER
        user = User.query.get(1)
        self.assertEqual(len(user.wallets), 1)

    def test_create_wallet_empty_error(self):
        result = self._create_wallet("", "", "", "")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)

    def test_create_wallet_failed(self):
        # create user first
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            msisdn='081219644314',
        )
        user.set_password("password")
        db.session.add(user)

        # generate mock up responses
        expected_value = {
            "status" : "009",
            "message" : "Unexpected Error"
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        #create actual wallet
        result = self._create_wallet("rose", "081219644314", "123456", "1")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)
        self.assertEqual(response["data"], "Virtual Account Creation Failed")

    def test_wallet_list(self):
        # add user first
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            msisdn='081219644314',
        )
        user.set_password("password")
        db.session.add(user)

        # generate mock responses
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        # create actual wallet
        result = self._create_wallet("rose", "081219644314", "123456", "1")
        response = result.get_json()

        # generate mock responses
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        # create actual wallet
        result = self._create_wallet("rose", "081219644314", "123456", "1")
        response = result.get_json()

        result = self._get_wallet_list("1")
        response = result.get_json()

        # CHECK WALLET IN DATABASES
        wallet = Wallet.query.filter_by(user_id=1)
        test = WalletSchema(many=True).dump(wallet).data

        self.assertEqual(response["status_code"], 0)
        self.assertEqual(len(response["data"]), len(test))

    def test_deposit_wallet(self):
        # add user first
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            msisdn='081219644314',
        )
        user.set_password("password")
        db.session.add(user)

        # generate mock responses
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        # create actual wallet
        result = self._create_wallet("rose", "081219644314", "123456", "1")
        response = result.get_json()

        wallet_id = response["data"]["wallet_id"]

        # deposit balance
        result = self._deposit(wallet_id, "9999")
        response = result.get_json()

        # CHECK BALANCE ON DATABASES
        wallet = Wallet.query.filter_by(id=wallet_id).first()
        self.assertEqual( wallet.balance, 9999)

        # CHECK TRANSACTION
        transaction = Transaction.query.filter_by(destination_id=wallet_id).first()
        self.assertEqual( transaction.amount, 9999)

    def test_transaction_history(self):
        # create user first
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            msisdn='081219644314',
        )
        user.set_password("password")
        db.session.add(user)

        # generate mock response
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        # create actual wallet
        result = self._create_wallet("rose", "081219644314", "123456", "1")
        response = result.get_json()

        wallet_id = response["data"]["wallet_id"]

        # deposit balance
        result = self._deposit(wallet_id, "9999")

        # checking transaction history
        result = self._transaction_history(wallet_id)
        response = result.get_json()

        self.assertEqual(response["status_code"], 0)
        self.assertEqual(len(response["data"]), 1)

    def test_wallet_details_success(self):
        # create user first
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            msisdn='081219644314',
        )
        user.set_password("password")
        db.session.add(user)

        # generate mock response
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        # create actual wallet
        result = self._create_wallet("rose", "081219644314", "123456", "1")
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
        # create user first
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            msisdn='081219644314',
        )
        user.set_password("password")
        db.session.add(user)

        # generate mock response
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        # create actual wallet
        result = self._create_wallet("rose", "081219644314", "123456", "1")
        response = result.get_json()

        wallet_id = response["data"]["wallet_id"]

        # CHECK WALLET DETAILS
        result = self._get_wallet_details(wallet_id, "122456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)

    def test_wallet_remove(self):
        # create user first
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            msisdn='081219644314',
        )
        user.set_password("password")
        db.session.add(user)

        # generate mock response
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        # create actual wallet
        result = self._create_wallet("rose", "081219644314", "123456", "1")
        response = result.get_json()

        # create actual wallet
        result = self._create_wallet("rose", "081219644314", "123456", "1")
        response = result.get_json()

        wallet_id = response["data"]["wallet_id"]

        result = self._remove_wallet(wallet_id, "123456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 0)

        result = self._get_wallet_list("1")
        response = result.get_json()

        self.assertEqual(len(response["data"]), 1)

    def test_wallet_remove_failed(self):
        # create user first
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            msisdn='081219644314',
        )
        user.set_password("password")
        db.session.add(user)

        # generate mock response
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        # create actual wallet
        result = self._create_wallet("rose", "081219644314", "123456", "1")
        response = result.get_json()

        wallet_id = response["data"]["wallet_id"]

        result = self._remove_wallet(wallet_id, "123456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)

    def test_wallet_remove_failed_not_found(self):
        # GENERATE WALLET FIRST
        result = self._remove_wallet("123", "123456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 404)

    def test_check_wallet_balance_success(self):
        # create user first
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            msisdn='081219644314',
        )
        user.set_password("password")
        db.session.add(user)

        # generate mock response
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        # create actual wallet
        result = self._create_wallet("rose", "081219644314", "123456", "1")
        response = result.get_json()

        wallet_id = response["data"]["wallet_id"]

        result = self._check_balance(wallet_id, "123456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 0)
        self.assertEqual(response["data"]["balance"], 0)

    def test_check_wallet_balance_failed(self):
        # create user first
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            msisdn='081219644314',
        )
        user.set_password("password")
        db.session.add(user)

        # generate mock response
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        # create actual wallet
        result = self._create_wallet("rose", "081219644314", "123456", "1")
        response = result.get_json()

        wallet_id = response["data"]["wallet_id"]

        result = self._check_balance("123213", "213456")
        response = result.get_json()

        self.assertEqual(response["status_code"], 404)

if __name__ == "__main__":
    unittest.main(verbosity=2)
