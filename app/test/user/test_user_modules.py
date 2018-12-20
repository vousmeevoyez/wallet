import sys
from unittest.mock import Mock, patch

from app.api.wallet import helper

from app.test.base          import BaseTestCase
from app.api.user.modules   import user, bank_account
from app.api.errors         import *

from app.api.config import config

RESPONSE_MSG = config.Config.RESPONSE_MSG

class TestUserModules(BaseTestCase):

    def test_user_register_success(self):
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
        result = user.UserController().user_register(params)
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["CREATE_USER"])

    def test_user_register_failed_duplicate(self):
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
        result = user.UserController().user_register(params)
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["CREATE_USER"])

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
        result = user.UserController().user_register(params)
        self.assertEqual(result[0]["errors"], RESPONSE_MSG["FAILED"]["ERROR_ADDING_RECORD"])

    def test_user_list_success(self):
        params = {
        }
        result = user.UserController().user_list(params)
        self.assertTrue(len(result["data"]) > 0)

    def test_user_info_success(self):
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
        result = user.UserController().user_register(params)
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["CREATE_USER"])

        params = {
            "user_id" : result["data"]["user_id"]
        }
        result = user.UserController().user_info(params)
        self.assertTrue(result["data"]["user_information"])
        self.assertTrue(result["data"]["wallet_information"])

    def test_user_info_failed_record_not_found(self):
        params = {
            "user_id" : 123
        }
        result = user.UserController().user_info(params)
        self.assertEqual(result[0]["errors"], RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])

    def test_remove_user_success(self):
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
        result = user.UserController().user_register(params)
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["CREATE_USER"])

        result = user.UserController().remove_user({"user_id" : result["data"]["user_id"]})
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["REMOVE_USER"])

    def test_remove_user_failed_not_found(self):
        params = {
            "user_id" : 123
        }
        result = user.UserController().remove_user(params)
        self.assertEqual(result[0]["errors"], RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])


class TestUserBankAccountModules(BaseTestCase):

    def test_add_bank_account_success(self):
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
        result = user.UserController().user_register(params)
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["CREATE_USER"])

        params = {
            "user_id"   : result["data"]["user_id"],
            "bank_code" : "009",
            "label"     : "sample label",
            "name"      : "jennie",
            "account_no": "1234567891",
        }
        result = bank_account.UserBankAccountController().add(params)
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["CREATE_BANK_ACCOUNT"])

    def test_add_bank_account_failed_user_not_found(self):
        params = {
            "user_id"   : 1234,
            "bank_code" : "009",
            "label"     : "sample label",
            "name"      : "jennie",
            "account_no": "1234567891",
        }
        result = bank_account.UserBankAccountController().add(params)
        self.assertEqual(result[0]["errors"], RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])

    def test_add_bank_account_failed_user_not_found(self):
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
        result = user.UserController().user_register(params)
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["CREATE_USER"])

        params = {
            "user_id"   : result["data"]["user_id"],
            "bank_code" : "666",
            "label"     : "sample label",
            "name"      : "jennie",
            "account_no": "1234567891",
        }
        result = bank_account.UserBankAccountController().add(params)
        self.assertEqual(result[0]["errors"], RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])

    def test_show_bank_account_success(self):
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
        result = user.UserController().user_register(params)
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["CREATE_USER"])

        params = {
            "user_id"   : result["data"]["user_id"],
        }
        result = bank_account.UserBankAccountController().show(params)
        self.assertEqual(len(result["data"]) ,0)

    def test_show_bank_account_failed_record_not_found(self):
        params = {
            "user_id"   : 123,
        }
        result = bank_account.UserBankAccountController().show(params)
        self.assertEqual(result[0]["errors"], RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])

    def test_update_bank_account_success(self):
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
        result = user.UserController().user_register(params)
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["CREATE_USER"])

        user_id = result["data"]["user_id"]

        params = {
            "user_id"   : user_id,
            "bank_code" : "009",
            "label"     : "sample label",
            "name"      : "jennie",
            "account_no": "1234567891",
        }
        result = bank_account.UserBankAccountController().add(params)
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["CREATE_BANK_ACCOUNT"])

        params = {
            "user_id"   : user_id,
        }
        result = bank_account.UserBankAccountController().show(params)
        self.assertEqual(len(result["data"]) ,1)

        user_bank_account_id = result["data"][0]["id"]

        params = {
            "user_bank_account_id" : user_bank_account_id,
            "user_id"   : user_id,
            "bank_code" : "009",
            "label"     : "my label",
            "name"      : "jennie",
            "account_no": "1234567891",
        }
        result = bank_account.UserBankAccountController().update(params)
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["UPDATE_BANK_ACCOUNT"])

    def test_update_bank_account_failed_bank_account_not_found(self):
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
        result = user.UserController().user_register(params)
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["CREATE_USER"])

        user_id = result["data"]["user_id"]

        params = {
            "user_id"   : user_id,
            "bank_code" : "009",
            "label"     : "sample label",
            "name"      : "jennie",
            "account_no": "1234567891",
        }
        result = bank_account.UserBankAccountController().add(params)
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["CREATE_BANK_ACCOUNT"])

        params = {
            "user_id"   : user_id,
        }
        result = bank_account.UserBankAccountController().show(params)
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
        result = bank_account.UserBankAccountController().update(params)
        self.assertEqual(result[0]["errors"], RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])


    def test_update_bank_account_failed_bank_not_found(self):
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
        result = user.UserController().user_register(params)
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["CREATE_USER"])

        user_id = result["data"]["user_id"]

        params = {
            "user_id"   : user_id,
            "bank_code" : "009",
            "label"     : "sample label",
            "name"      : "jennie",
            "account_no": "1234567891",
        }
        result = bank_account.UserBankAccountController().add(params)
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["CREATE_BANK_ACCOUNT"])

        params = {
            "user_id"   : user_id,
        }
        result = bank_account.UserBankAccountController().show(params)
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
        result = bank_account.UserBankAccountController().update(params)
        self.assertEqual(result[0]["errors"], RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])

    def test_remove_bank_account_success(self):
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
        result = user.UserController().user_register(params)
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["CREATE_USER"])

        user_id = result["data"]["user_id"]

        params = {
            "user_id"   : user_id,
            "bank_code" : "009",
            "label"     : "sample label",
            "name"      : "jennie",
            "account_no": "1234567891",
        }
        result = bank_account.UserBankAccountController().add(params)
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["CREATE_BANK_ACCOUNT"])

        params = {
            "user_id"   : user_id,
        }
        result = bank_account.UserBankAccountController().show(params)
        self.assertEqual(len(result["data"]) ,1)

        user_bank_account_id = result["data"][0]["id"]

        result = bank_account.UserBankAccountController().remove({"user_bank_account_id" : user_bank_account_id, "user_id" : user_id })
        self.assertEqual(result["message"], RESPONSE_MSG["SUCCESS"]["REMOVE_BANK_ACCOUNT"])
