import sys
import unittest
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

class TestTransferRoutes(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    """
        HELPER
    """

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
        pass
        #result = self._direct_transfer("label", "jennie", 525600, "jennie", "password")
        #response = result.get_json()

        #self.assertEqual(response["data"], "Secret key successfully created")
        #self.assertEqual(response["status_code"], 0)
        #self.assertEqual(response["status_message"], "SUCCESS")

    def test_bulk_transfer(self):
        source = "12345"
        transaction_list = [
            {
                "destination" : "123",
                "amount"      : 1,
                "notes"       : "SALARY DISTRIBUTION"
            },
            {
                "destination" : "124",
                "amount"      : 1,
                "notes"       : "SALARY DISTRIBUTION"
            }
        ]
        #result = self._bulk_transfer(source, transaction_list, "123456")
        #response = result.get_json()

        #self.assertEqual(response["data"], "Secret key successfully created")
        #self.assertEqual(response["status_code"], 0)
        #self.assertEqual(response["status_message"], "SUCCESS")


if __name__ == "__main__":
    unittest.main(verbosity=2)
