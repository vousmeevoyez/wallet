""" 
    Test User Bank Account SErvices
"""
from app.api.wallet import helper

from app.test.base          import BaseTestCase
from app.api.errors         import *

from app.api.user.modules.user_services import UserServices
from app.api.user.modules.bank_account_services import BankAccountServices

from app.api.config import config

RESPONSE_MSG = config.Config.RESPONSE_MSG

class TestUserBankAccountServices(BaseTestCase):
    """ Test Class for User Bank Account Services"""

    def test_add_bank_account_success(self):
        """ test add bank account """
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
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["CREATE_USER"])

        params = {
            "user_id"   : result["data"]["user_id"],
            "bank_code" : "9",
            "label"     : "sample label",
            "name"      : "jennie",
            "account_no": "1234567891",
        }
        result = BankAccountServices().add(params)
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["CREATE_BANK_ACCOUNT"])

    def test_add_bank_account_failed_user_not_found(self):
        """ test add bank account but not found"""
        params = {
            "user_id"   : 1234,
            "bank_code" : "9",
            "label"     : "sample label",
            "name"      : "jennie",
            "account_no": "1234567891",
        }
        result = BankAccountServices().add(params)
        self.assertEqual(result[0]["errors"], RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])

    def test_add_bank_account_failed_user_not_found(self):
        """ test add bank account but bank not found"""
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
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["CREATE_USER"])

        params = {
            "user_id"   : result["data"]["user_id"],
            "bank_code" : "666",
            "label"     : "sample label",
            "name"      : "jennie",
            "account_no": "1234567891",
        }
        result = BankAccountServices().add(params)
        self.assertEqual(result[0]["errors"], RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])

    def test_show_bank_account_success(self):
        """ test function that show all bank account"""
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
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["CREATE_USER"])

        params = {
            "user_id"   : result["data"]["user_id"],
        }
        result = BankAccountServices().show(params)
        self.assertEqual(len(result["data"]) ,0)

    def test_show_bank_account_failed_record_not_found(self):
        """ test function that show all bank account but user not found"""
        params = {
            "user_id"   : 123,
        }
        result = BankAccountServices().show(params)
        self.assertEqual(result[0]["errors"], RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])

    def test_update_bank_account_success(self):
        """ test function that update bank account information"""
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
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["CREATE_USER"])

        user_id = result["data"]["user_id"]

        params = {
            "user_id"   : user_id,
            "bank_code" : "9",
            "label"     : "sample label",
            "name"      : "jennie",
            "account_no": "1234567891",
        }
        result = BankAccountServices().add(params)
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["CREATE_BANK_ACCOUNT"])

        params = {
            "user_id"   : user_id,
        }
        result = BankAccountServices().show(params)
        self.assertEqual(len(result["data"]) ,1)

        user_bank_account_id = result["data"][0]["id"]

        params = {
            "user_bank_account_id" : user_bank_account_id,
            "user_id"   : user_id,
            "bank_code" : "9",
            "label"     : "my label",
            "name"      : "jennie",
            "account_no": "1234567891",
        }
        result = BankAccountServices().update(params)
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["UPDATE_BANK_ACCOUNT"])

    def test_update_bank_account_failed_bank_account_not_found(self):
        """ test function to update bank account information but account not
        found"""
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
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["CREATE_USER"])

        user_id = result["data"]["user_id"]

        params = {
            "user_id"   : user_id,
            "bank_code" : "9",
            "label"     : "sample label",
            "name"      : "jennie",
            "account_no": "1234567891",
        }
        result = BankAccountServices().add(params)
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["CREATE_BANK_ACCOUNT"])

        params = {
            "user_id"   : user_id,
        }
        result = BankAccountServices().show(params)
        self.assertEqual(len(result["data"]) ,1)

        user_bank_account_id = result["data"][0]["id"]

        params = {
            "user_bank_account_id" : 1234,
            "user_id"   : user_id,
            "bank_code" : "004",
            "label"     : "my label",
            "name"      : "jennie",
            "account_no": "1234567891",
        }
        result = BankAccountServices().update(params)
        self.assertEqual(result[0]["errors"], RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])


    def test_update_bank_account_failed_bank_not_found(self):
        """ test update bank account but bank no tofund"""
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
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["CREATE_USER"])

        user_id = result["data"]["user_id"]

        params = {
            "user_id"   : user_id,
            "bank_code" : "9",
            "label"     : "sample label",
            "name"      : "jennie",
            "account_no": "1234567891",
        }
        result = BankAccountServices().add(params)
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["CREATE_BANK_ACCOUNT"])

        params = {
            "user_id"   : user_id,
        }
        result = BankAccountServices().show(params)
        self.assertEqual(len(result["data"]) ,1)

        user_bank_account_id = result["data"][0]["id"]

        params = {
            "user_bank_account_id" : 1234,
            "user_id"   : user_id,
            "bank_code" : "000",
            "label"     : "my label",
            "name"      : "jennie",
            "account_no": "1234567891",
        }
        result = BankAccountServices().update(params)
        self.assertEqual(result[0]["errors"], RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])

    def test_remove_bank_account_success(self):
        """ tst function to remove bank account """
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
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["CREATE_USER"])

        user_id = result["data"]["user_id"]

        params = {
            "user_id"   : user_id,
            "bank_code" : "9",
            "label"     : "sample label",
            "name"      : "jennie",
            "account_no": "1234567891",
        }
        result = BankAccountServices().add(params)
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["CREATE_BANK_ACCOUNT"])

        params = {
            "user_id"   : user_id,
        }
        result = BankAccountServices().show(params)
        self.assertEqual(len(result["data"]) ,1)

        user_bank_account_id = result["data"][0]["id"]

        result = BankAccountServices().remove({"user_bank_account_id" : user_bank_account_id, "user_id" : user_id })
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["REMOVE_BANK_ACCOUNT"])
