""" 
    Test User Bank Account SErvices
"""
from app.api.wallet import helper

from app.test.base          import BaseTestCase
from app.api.http_response  import *

from app.api.user.modules.user_services import UserServices
from app.api.user.modules.bank_account_services import BankAccountServices

from app.config import config

ERROR = config.Config.ERROR_HEADER

class TestUserBankAccountServices(BaseTestCase):
    """ Test Class for User Bank Account Services"""

    def test_add_bank_account_success(self):
        """ test add bank account """
        params = {
            "user_id"   : 2,
            "bank_code" : "009",
            "label"     : "sample label",
            "name"      : "jennie",
            "account_no": "1234567891",
        }
        result = BankAccountServices().add(params)
        self.assertEqual(result[1], 201)

    def test_add_bank_account_failed_user_not_found(self):
        """ test add bank account but not found"""
        params = {
            "user_id"   : 1234,
            "bank_code" : "009",
            "label"     : "sample label",
            "name"      : "jennie",
            "account_no": "1234567891",
        }
        result = BankAccountServices().add(params)
        self.assertEqual(result[0]["error"], ERROR["USER_NOT_FOUND"])
        self.assertEqual(result[1], 404)

    def test_add_bank_account_failed_bank_not_found(self):
        """ test add bank account but bank not found"""
        params = {
            "user_id"   : 2,
            "bank_code" : "666",
            "label"     : "sample label",
            "name"      : "jennie",
            "account_no": "1234567891",
        }
        result = BankAccountServices().add(params)
        self.assertEqual(result[0]["error"], ERROR["BANK_NOT_FOUND"])
        self.assertEqual(result[1], 404)

    def test_show_bank_account_success(self):
        """ test function that show all bank account"""
        params = {
            "user_id" : 2,
        }
        result = BankAccountServices().show(params)
        self.assertEqual(len(result), 0)

    def test_show_bank_account_failed_record_not_found(self):
        """ test function that show all bank account but user not found"""
        params = {
            "user_id" : 123,
        }
        result = BankAccountServices().show(params)
        self.assertEqual(result[0]["error"], ERROR["USER_NOT_FOUND"])
        self.assertEqual(result[1], 404)

    def test_update_bank_account_success(self):
        """ test function that update bank account information"""
        params = {
            "user_id"   : 2,
            "bank_code" : "009",
            "label"     : "sample label",
            "name"      : "jennie",
            "account_no": "1234567891",
        }
        result = BankAccountServices().add(params)
        self.assertEqual(result[1], 201)

        params = {
            "user_id" : 2,
        }
        result = BankAccountServices().show(params)
        self.assertEqual(len(result), 1)

        user_bank_account_id = result[0]["id"]

        params = {
            "user_bank_account_id" : user_bank_account_id,
            "user_id"   : 2,
            "bank_code" : "009",
            "label"     : "my label",
            "name"      : "jennie",
            "account_no": "1234567891",
        }
        result = BankAccountServices().update(params)
        self.assertEqual(result[1], 204)

    def test_update_bank_account_failed_bank_account_not_found(self):
        """ test function to update bank account information but account not
        found"""
        params = {
            "user_id"   : 2,
            "bank_code" : "009",
            "label"     : "sample label",
            "name"      : "jennie",
            "account_no": "1234567891",
        }
        result = BankAccountServices().add(params)
        self.assertEqual(result[1], 201)

        params = {
            "user_id" : 2,
        }
        result = BankAccountServices().show(params)
        self.assertEqual(len(result), 1)

        params = {
            "user_bank_account_id" : 1234,
            "user_id"   : 2,
            "bank_code" : "004",
            "label"     : "my label",
            "name"      : "jennie",
            "account_no": "1234567891",
        }
        result = BankAccountServices().update(params)
        self.assertEqual(result[0]["error"], ERROR["BANK_ACC_NOT_FOUND"])
        self.assertEqual(result[1], 404)

    def test_update_bank_account_failed_bank_not_found(self):
        """ test update bank account but bank no tofund"""
        params = {
            "user_id"   : 2,
            "bank_code" : "009",
            "label"     : "sample label",
            "name"      : "jennie",
            "account_no": "1234567891",
        }
        result = BankAccountServices().add(params)
        self.assertEqual(result[1], 201)

        params = {
            "user_id" : 2,
        }
        result = BankAccountServices().show(params)
        self.assertEqual(len(result), 1)

        user_bank_account_id = result[0]["id"]

        params = {
            "user_bank_account_id" : 1234,
            "user_id"   : 2,
            "bank_code" : "000",
            "label"     : "my label",
            "name"      : "jennie",
            "account_no": "1234567891",
        }
        result = BankAccountServices().update(params)
        self.assertEqual(result[0]["error"], ERROR["BANK_ACC_NOT_FOUND"])

    def test_remove_bank_account_success(self):
        """ tst function to remove bank account """
        params = {
            "user_id"   : 2,
            "bank_code" : "009",
            "label"     : "sample label",
            "name"      : "jennie",
            "account_no": "1234567891",
        }
        result = BankAccountServices().add(params)
        self.assertEqual(result[1], 201)

        params = {
            "user_id" : 2,
        }
        result = BankAccountServices().show(params)
        self.assertEqual(len(result) ,1)

        user_bank_account_id = result[0]["id"]

        result = BankAccountServices().remove({"user_bank_account_id" :
                                               user_bank_account_id, "user_id"
                                               : 2})
        self.assertEqual(result[1], 204)
