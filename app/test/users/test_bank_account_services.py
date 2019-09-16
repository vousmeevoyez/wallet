"""
    Test User Bank Account SErvices
"""
import uuid
from app.test.base import BaseTestCase

from app.api.users.modules.bank_account_services import BankAccountServices

from app.api.models import BankAccount

from app.config import config

from app.api.error.http import *

fake_uuid = str(uuid.uuid4())


class TestUserBankAccountServices(BaseTestCase):
    """ Test Class for User Bank Account Services"""

    def test_add_bank_account_success(self):
        """ test add bank account """
        params = {"label": "sample label", "name": "jennie", "account_no": "1234567891"}
        bank_account = BankAccount(**params)

        result = BankAccountServices(str(self.user.id), "009").add(bank_account)
        self.assertEqual(result[1], 201)

    def test_add_bank_account_failed_user_not_found(self):
        """ test add bank account but not found"""
        params = {"label": "sample label", "name": "jennie", "account_no": "1234567891"}
        bank_account = BankAccount(**params)

        with self.assertRaises(RequestNotFound):
            result = BankAccountServices(fake_uuid, "009").add(bank_account)

    def test_add_bank_account_failed_bank_not_found(self):
        """ test add bank account but bank not found"""
        params = {"label": "sample label", "name": "jennie", "account_no": "1234567891"}
        bank_account = BankAccount(**params)

        with self.assertRaises(RequestNotFound):
            result = BankAccountServices(str(self.user.id), fake_uuid).add(bank_account)

    def test_show_bank_account_success(self):
        """ test function that show all bank account"""
        result = BankAccountServices(str(self.user.id)).show()
        self.assertEqual(len(result), 0)

    def test_show_bank_account_failed_record_not_found(self):
        """ test function that show all bank account but user not found"""
        with self.assertRaises(RequestNotFound):
            result = BankAccountServices(fake_uuid).show()

    def test_update_bank_account_success(self):
        """ test function that update bank account information"""
        params = {"label": "sample label", "name": "jennie", "account_no": "1234567891"}
        bank_account = BankAccount(**params)

        result = BankAccountServices(str(self.user.id), "009").add(bank_account)
        self.assertEqual(result[1], 201)

        result = BankAccountServices(str(self.user.id)).show()
        self.assertEqual(len(result), 1)

        user_bank_account_id = result[0]["id"]

        params = {"label": "my label", "name": "jennie", "account_no": "1234567891"}
        result = BankAccountServices(
            str(self.user.id), "009", user_bank_account_id
        ).update(params)

        self.assertEqual(result[1], 204)

    def test_update_bank_account_failed_bank_account_not_found(self):
        """ test function to update bank account information but account not
        found"""
        params = {"label": "sample label", "name": "jennie", "account_no": "1234567891"}
        bank_account = BankAccount(**params)

        result = BankAccountServices(str(self.user.id), "009").add(bank_account)
        self.assertEqual(result[1], 201)

        result = BankAccountServices(str(self.user.id)).show()
        self.assertEqual(len(result), 1)

        params = {"label": "my label", "name": "jennie", "account_no": "1234567891"}
        with self.assertRaises(RequestNotFound):
            result = BankAccountServices(str(self.user.id), "009", fake_uuid).update(
                params
            )

    def test_update_bank_account_failed_bank_not_found(self):
        """ test update bank account but bank no tofund"""
        params = {"label": "sample label", "name": "jennie", "account_no": "1234567891"}
        bank_account = BankAccount(**params)

        result = BankAccountServices(str(self.user.id), "009").add(bank_account)
        self.assertEqual(result[1], 201)

        result = BankAccountServices(str(self.user.id)).show()
        self.assertEqual(len(result), 1)

        user_bank_account_id = result[0]["id"]

        params = {"label": "my label", "name": "jennie", "account_no": "1234567891"}
        with self.assertRaises(RequestNotFound):
            result = BankAccountServices(str(self.user.id), "009", fake_uuid).update(
                params
            )

    def test_remove_bank_account_success(self):
        """ tst function to remove bank account """
        params = {"label": "sample label", "name": "jennie", "account_no": "1234567891"}
        bank_account = BankAccount(**params)

        result = BankAccountServices(str(self.user.id), "009").add(bank_account)
        self.assertEqual(result[1], 201)

        result = BankAccountServices(str(self.user.id)).show()
        self.assertEqual(len(result), 1)

        user_bank_account_id = result[0]["id"]

        result = BankAccountServices(
            str(self.user.id), None, user_bank_account_id
        ).remove()
        self.assertEqual(result[1], 204)
