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

class TestAccessKeyRoutes(unittest.TestCase):

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

    def _create_access_key(self, label, name, expiration, username, password):
        return self.client.post(
            '/access_key/create',
            data=dict(
                label=label,
                name=name,
                expiration=expiration,
                username=username,
                password=password
            )
        )

    def _get_access_key_list(self):
        return self.client.get(
            '/access_key/list',
        )

    def _check_access_key(self, access_id):
        return self.client.get(
            '/access_key/check?id=' + access_id,
        )

    def _revoke_access_key(self, access_id):
        return self.client.get(
            '/access_key/revoke?id=' + access_id,
        )

    def _remove_access_key(self, access_id):
        return self.client.get(
            '/access_key/remove?id=' + access_id,
        )

    """
        ACCESS KEY
    """

    def test_create_access_key_success(self):
        result = self._create_access_key("label", "jennie", 525600, "jennie", "password")
        response = result.get_json()

        self.assertEqual(response["data"], "Secret key successfully created")
        self.assertEqual(response["status_code"], 0)
        self.assertEqual(response["status_message"], "SUCCESS")

    def test_create_access_key_duplicate(self):
        result = self._create_access_key("label", "jennie", 525600, "jennie", "password")
        response = result.get_json()

        result = self._create_access_key("label", "jennie", 525600, "jennie", "password")
        response = result.get_json()

        self.assertEqual(response["data"], "Error adding record")
        self.assertEqual(response["status_code"], 400)

    def test_create_access_key_blank_label(self):
        result = self._create_access_key("", "jennie", 525600, "jennie", "password")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)
        self.assertEqual(response["data"], {'label': [' Data cannot be blank']} )

    def test_create_access_key_blank_name(self):
        result = self._create_access_key("label", "", 525600, "jennie", "password")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)
        self.assertEqual(response["data"], {'name': [' Data cannot be blank']})

    def test_create_access_key_blank_expiration(self):
        result = self._create_access_key("label", "jennie", 0, "jennie", "password")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)
        self.assertEqual(response["data"], {'expiration': ['Invalid Expiration, Cannot be less or equal 0']})

    def test_create_access_key_blank_username(self):
        result = self._create_access_key("label", "jennie", 1, "", "password")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)
        self.assertEqual(response["data"], {'username': [' Data cannot be blank']})

    def test_create_access_key_blank_password(self):
        result = self._create_access_key("label", "jennie", 1, "username", "")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)
        self.assertEqual(response["data"], {'password': [' Data cannot be blank']})

    def test_create_access_key_blank(self):
        result = self._create_access_key("", "", 0, "", "")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)
        self.assertEqual(response["data"], {'expiration': ['Invalid Expiration, Cannot be less or equal 0'], 'label': [' Data cannot be blank'], 'name': [' Data cannot be blank'], 'password': [' Data cannot be blank'], 'username': [' Data cannot be blank']})

    def test_get_access_key_list(self):
        result = self._get_access_key_list()
        response = result.get_json()

        self.assertEqual(response["status_code"], 0)
        self.assertEqual(response["data"], [])

    def test_check_access_key(self):
        result = self._check_access_key("123")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)
        self.assertEqual(response["data"], "INVALID TOKEN")

    def test_revoke_access_key(self):
        result = self._revoke_access_key("123")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)
        self.assertEqual(response["data"], "Item not found")

    def test_remove_access_key(self):
        result = self._remove_access_key("123")
        response = result.get_json()

        self.assertEqual(response["status_code"], 400)
        self.assertEqual(response["data"], "Item not found")

if __name__ == "__main__":
    unittest.main(verbosity=2)
