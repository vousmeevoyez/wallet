""" 
    Test User Services
"""
from app.test.base import BaseTestCase
from app.api.http_response import *

from app.api.users.modules.user_services import UserServices
from app.api.users.modules.bank_account_services import BankAccountServices

from app.api.models import *

from app.api.error.http import *

from app.config import config


class TestUserServices(BaseTestCase):
    """ Test User Services"""

    def test_user_add_success(self):
        """ Test add user """
        params = {
            "username": "jennie",
            "name": "jennie",
            "phone_ext": "62",
            "phone_number": "81212341235",
            "email": "jennie@blackpink.com",
            "role_id": 1,
        }
        user = User(**params)
        result = UserServices().add(user, "password", "123456", "LABEL")
        self.assertEqual(result[1], 201)  # created

    def test_user_add_failed_duplicate(self):
        """ test fail adding user by trying add same account"""
        params = {
            "username": "jennie",
            "name": "jennie",
            "phone_ext": "62",
            "phone_number": "81212341235",
            "email": "jennie@blackpink.com",
            "role_id": 1,
        }
        user = User(**params)
        result = UserServices().add(user, "password", "123456", "LABEL")

        self.assertEqual(result[1], 201)  # created

        params = {
            "username": "jennie",
            "name": "jennie",
            "phone_ext": "62",
            "phone_number": "81212341235",
            "email": "jennie@blackpink.com",
            "role_id": 1,
        }
        user = User(**params)
        with self.assertRaises(UnprocessableEntity):
            result = UserServices().add(user, "password", "123456", "LABEL")

    def test_user_list_success(self):
        """ test get list of users"""
        result = UserServices().show({})
        self.assertTrue(len(result) > 0)

    def test_user_info_success(self):
        """ test get single user info"""
        params = {
            "username": "jennie",
            "name": "jennie",
            "phone_ext": "62",
            "phone_number": "81212341235",
            "email": "jennie@blackpink.com",
            "role_id": 1,
        }
        user = User(**params)
        result = UserServices().add(user, "password", "123456", "LABEL")
        self.assertEqual(result[1], 201)  # created

        user_id = result[0]["data"]["user_id"]
        result = UserServices(user_id).info()
        self.assertTrue(result[0]["data"])

    def test_user_info_failed_record_not_found(self):
        """ test get single user info but user not found"""
        with self.assertRaises(BadRequest):
            result = UserServices("12345").info()

    def test_remove_user_success(self):
        """ test removing user """
        params = {
            "username": "jennie",
            "name": "jennie",
            "phone_ext": "62",
            "phone_number": "81212341235",
            "email": "jennie@blackpink.com",
            "role_id": 1,
        }
        user = User(**params)
        result = UserServices().add(user, "password", "123456", "LABEL")
        self.assertEqual(result[1], 201)  # created

        user_id = result[0]["data"]["user_id"]

        result = UserServices(user_id).remove()
        self.assertEqual(result[1], 204)  # no content

        with self.assertRaises(RequestNotFound):
            result = UserServices(user_id).info()

    def test_remove_user_failed_not_found(self):
        """ test removing user but not found"""
        with self.assertRaises(BadRequest):
            result = UserServices("1234").info()

    def test_update_user_success(self):
        """ test updating user information """
        params = {
            "username": "jennie",
            "name": "jennie",
            "phone_ext": "62",
            "phone_number": "81212341235",
            "email": "jennie@blackpink.com",
            "role_id": 1,
        }
        user = User(**params)
        result = UserServices().add(user, "password", "123456", "LABEL")
        self.assertEqual(result[1], 201)  # created

        user_id = result[0]["data"]["user_id"]

        params = {
            "name": "jisooo",
            "phone_ext": "62",
            "phone_number": "81212222222",
            "email": "jisooo@blackpink.com",
            "password": "password",
        }

        result = UserServices(user_id).update(params)
        self.assertEqual(result[1], 204)

        result = UserServices(user_id).info()

    def test_update_user_old(self):
        """ test updating user information """
        params = {
            "username": "jennie",
            "name": "jennie",
            "phone_ext": "62",
            "phone_number": "81212341235",
            "email": "jennie@blackpink.com",
            "role_id": 1,
        }
        user = User(**params)
        result = UserServices().add(user, "password", "123456", "LABEL")
        self.assertEqual(result[1], 201)  # created

        user_id = result[0]["data"]["user_id"]

        params = {
            "name": "jennie",
            "phone_ext": "62",
            "phone_number": "81212341235",
            "email": "jennie@blackpink.com",
        }
        with self.assertRaises(UnprocessableEntity):
            result = UserServices(user_id).update(params)
