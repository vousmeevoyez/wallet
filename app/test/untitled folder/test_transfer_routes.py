import sys
import unittest
import json

from unittest.mock import Mock, patch

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

class TestTransferRoutes(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.client = self.app.test_client()
        self.mock_post_patcher = patch("app.bank.utility.remote_call.requests.post")
        self.mock_post = self.mock_post_patcher.start()

        self._init_test()
    #end def

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

        self.mock_post_patcher.stop()
    #end def

    def _init_test(self):
        # we create 2 dummy user & wallet to simulate transfer between user
        # create first user 
        self.user = User(
            username='dummyacc1',
            name='dummyacc1',
            email='dummyacc1@test.com',
            msisdn='081209644314',
        )
        self.user.set_password("password")
        db.session.add(self.user)
        db.session.commit()

        # create first wallet user
        self.wallet = Wallet(
            user_id=self.user.id,
            balance=100
        )
        self.wallet.set_pin("123456")
        db.session.add(self.wallet)
        db.session.commit()

        # create second user
        self.user2 = User(
            username='dummyacc2',
            name='dummyacc2',
            email='dummyacc2@test.com',
            msisdn='081229644310',
        )
        self.user2.set_password("password")
        db.session.add(self.user2)
        db.session.commit()

        # create second wallet user
        self.wallet2 = Wallet(
            user_id=self.user2.id,
            balance=100
        )
        self.wallet2.set_pin("123456")
        db.session.add(self.wallet2)
        db.session.commit()

        # GET ACCESS TOKEN
        response = self._request_token("dummyacc1", "password")
        result = response.get_json()
        self.access_token = result["data"]["access_token"]
    #end def

    """
        HELPER
    """
    def _direct_transfer(self, access_token, source, destination, amount, notes, pin):
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.post(
            '/transfer/direct',
            data=dict(
                source=source,
                destination=destination,
                amount=amount,
                notes=notes,
                pin=pin
            ),
            headers=headers
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

    def _request_token(self, username, password):
        return self.client.post(
            '/auth/request_token',
            data=dict(
                username=username,
                password=password
            )
        )


    """
        TRANFSER
    """

    def test_direct_transfer_success(self):
        response = self._direct_transfer(self.access_token, self.wallet.id, self.wallet2.id, "1", "TEST", "123456")
        result = response.get_json()
        self.assertEqual(result["status_code"], 0)

    def test_direct_transfer_failed_destination_not_found(self):
        response = self._direct_transfer(self.access_token, self.wallet.id, "3", "1", "TEST", "123456")
        result = response.get_json()
        self.assertEqual(result["status_code"], 404)

    def test_direct_transfer_failed_source_not_found(self):
        response = self._direct_transfer(self.access_token, "3", self.wallet2.id, "1", "TEST", "123456")
        result = response.get_json()
        self.assertEqual(result["status_code"], 400)

    def test_direct_transfer_pin_failed(self):
        response = self._direct_transfer(self.access_token, self.wallet.id, self.wallet2.id, "1", "TEST", "103456")
        result = response.get_json()
        self.assertEqual(result["status_code"], 400)

if __name__ == "__main__":
    unittest.main(verbosity=2)
