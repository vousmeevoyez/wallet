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

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

        self.mock_post_patcher.stop()


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
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            msisdn='081219644314',
        )
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        wallet = Wallet(
            user_id=user.id,
            balance=100
        )
        wallet.set_pin("123456")
        db.session.add(wallet)
        db.session.commit()

        user2 = User(
            username='jennie',
            name='jennie',
            email='jennie@bp.com',
            msisdn='081229644314',
        )
        user2.set_password("password")
        db.session.add(user2)
        db.session.commit()

        wallet2 = Wallet(
            user_id=user2.id,
            balance=100
        )
        wallet2.set_pin("123456")
        db.session.add(wallet2)
        db.session.commit()

        # GET ACCESS TOKEN
        response = self._request_token("lisabp", "password")
        result = response.get_json()
        access_token = result["data"]["access_token"]

        response = self._direct_transfer(access_token, wallet.id, wallet2.id, "1", "TEST", "123456")
        result = response.get_json()
        self.assertEqual(result["status_code"], 0)

    def test_direct_transfer_failed_destination_not_found(self):
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            msisdn='081219644314',
        )
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        wallet = Wallet(
            user_id=user.id,
            balance=100
        )
        wallet.set_pin("123456")
        db.session.add(wallet)
        db.session.commit()

        user2 = User(
            username='jennie',
            name='jennie',
            email='jennie@bp.com',
            msisdn='081229644314',
        )
        user2.set_password("password")
        db.session.add(user2)
        db.session.commit()

        wallet2 = Wallet(
            user_id=user2.id,
            balance=100
        )
        wallet2.set_pin("123456")
        db.session.add(wallet2)
        db.session.commit()

        # GET ACCESS TOKEN
        response = self._request_token("lisabp", "password")
        result = response.get_json()
        access_token = result["data"]["access_token"]

        response = self._direct_transfer(access_token, wallet.id, "3", "1", "TEST", "123456")
        result = response.get_json()
        self.assertEqual(result["status_code"], 404)

    def test_direct_transfer_failed_source_not_found(self):
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            msisdn='081219644314',
        )
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        wallet = Wallet(
            user_id=user.id,
            balance=100
        )
        wallet.set_pin("123456")
        db.session.add(wallet)
        db.session.commit()

        user2 = User(
            username='jennie',
            name='jennie',
            email='jennie@bp.com',
            msisdn='081229644314',
        )
        user2.set_password("password")
        db.session.add(user2)
        db.session.commit()

        wallet2 = Wallet(
            user_id=user2.id,
            balance=100
        )
        wallet2.set_pin("123456")
        db.session.add(wallet2)
        db.session.commit()

        # GET ACCESS TOKEN
        response = self._request_token("lisabp", "password")
        result = response.get_json()
        access_token = result["data"]["access_token"]

        response = self._direct_transfer(access_token, "3", wallet2.id, "1", "TEST", "123456")
        result = response.get_json()
        self.assertEqual(result["status_code"], 400)

    def test_direct_transfer_pin_failed(self):
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            msisdn='081219644314',
        )
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        wallet = Wallet(
            user_id=user.id,
            balance=100
        )
        wallet.set_pin("123456")
        db.session.add(wallet)
        db.session.commit()

        user2 = User(
            username='jennie',
            name='jennie',
            email='jennie@bp.com',
            msisdn='081229644314',
        )
        user2.set_password("password")
        db.session.add(user2)
        db.session.commit()

        wallet2 = Wallet(
            user_id=user2.id,
            balance=100
        )
        wallet2.set_pin("123456")
        db.session.add(wallet2)
        db.session.commit()

        # GET ACCESS TOKEN
        response = self._request_token("lisabp", "password")
        result = response.get_json()
        access_token = result["data"]["access_token"]

        response = self._direct_transfer(access_token, wallet.id, wallet2.id, "1", "TEST", "103456")
        result = response.get_json()
        self.assertEqual(result["status_code"], 400)

if __name__ == "__main__":
    unittest.main(verbosity=2)
