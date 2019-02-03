""" 
    Test User Services
"""
from app.api.wallet import helper

from app.test.base          import BaseTestCase
from app.api.http_response         import *

from app.api.user.modules.user_services import UserServices
from app.api.user.modules.bank_account_services import BankAccountServices

from app.config import config

RESPONSE_MSG = config.Config.RESPONSE_MSG

class TestUserServices(BaseTestCase):
    """ Test User Services"""

    def test_user_add_success(self):
        """ Test add user """
        params = {
            "username"    : "jennie",
            "name"        : "jennie",
            "phone_ext"   : "62",
            "phone_number": "81212341235",
            "email"       : "jennie@blackpink.com",
            "password"    : "password",
            "pin"         : "123456",
            "role"        : "USER",
        }
        result = UserServices().add(params)
        self.assertEqual(result[1], 201) # created

    def test_user_add_failed_duplicate(self):
        """ test fail adding user by trying add same account"""
        params = {
            "username"    : "jennie",
            "name"        : "jennie",
            "phone_ext"   : "62",
            "phone_number": "81212341235",
            "email"       : "jennie@blackpink.com",
            "password"    : "password",
            "pin"         : "123456",
            "role"        : "USER",
        }
        result = UserServices().add(params)
        self.assertEqual(result[1], 201) # created

        params = {
            "username"    : "jennie",
            "name"        : "jennie",
            "phone_ext"   : "62",
            "phone_number": "81212341235",
            "email"       : "jennie@blackpink.com",
            "password"    : "password",
            "pin"         : "123456",
            "role"        : "USER",
        }
        result = UserServices().add(params)
        self.assertEqual(result[1], 422)
        self.assertEqual(result[0]["error"], "DUPLICATE_USER")

    def test_user_list_success(self):
        """ test get list of users"""
        params = {
        }
        result = UserServices().show(params)
        self.assertTrue(len(result) > 0)

    def test_user_info_success(self):
        """ test get single user info"""
        params = {
            "username"    : "jennie",
            "name"        : "jennie",
            "phone_ext"   : "62",
            "phone_number": "81212341235",
            "email"       : "jennie@blackpink.com",
            "password"    : "password",
            "pin"         : "123456",
            "role"        : "USER",
        }
        result = UserServices().add(params)
        self.assertEqual(result[1], 201) # created

        params = {
            "user_id" : result[0]["user_id"]
        }
        result = UserServices().info(params)
        self.assertTrue(result["user_information"])
        #self.assertTrue(result["wallet_information"])

    def test_user_info_failed_record_not_found(self):
        """ test get single user info but user not found"""
        params = {
            "user_id" : 123
        }
        result = UserServices().info(params)
        self.assertEqual(result[1], 404)

    def test_remove_user_success(self):
        """ test removing user """
        params = {
            "username"    : "jennie",
            "name"        : "jennie",
            "phone_ext"   : "62",
            "phone_number": "81212341235",
            "email"       : "jennie@blackpink.com",
            "password"    : "password",
            "pin"         : "123456",
            "role"        : "USER",
        }
        result = UserServices().add(params)
        self.assertEqual(result[1], 201) # created

        user_id = result[0]["user_id"]

        result = UserServices().remove({"user_id" : user_id})
        self.assertEqual(result[1], 204) # no contento

        result = UserServices().info({"user_id" : user_id})
        self.assertEqual(result[1], 404)

    def test_remove_user_failed_not_found(self):
        """ test removing user but not found"""
        params = {
            "user_id" : 123
        }
        result = UserServices().remove(params)
        self.assertEqual(result[1], 404) # not found
