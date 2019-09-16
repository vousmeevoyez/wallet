"""
    Integration Testing between va & routes
"""
from unittest.mock import Mock, patch

from app.test.base import BaseTestCase

from app.api.models import VirtualAccount, VaLog
from app.api import db


class TestVaRoutes(BaseTestCase):
    """ Test Class for Wallet Routes"""

    def setUp(self):
        super().setUp()

        user1, wallet1 = self.create_dummy_user(self.access_token)

        self._user1 = user1
        self._wallet1 = wallet1

        user2, wallet2 = self.create_dummy_user(self.access_token)

        self._user2 = user2
        self._wallet2 = wallet2

    # end def

    """
        TEST VIRTUAL ACCOUNTS
    """

    def test_get_virtual_accounts(self):
        result = self.get_virtual_accounts(self.access_token)
        response = result.json
        self.assertEqual(len(response["data"]), 2)

    def test_get_virtual_account(self):
        result = self.get_virtual_accounts(self.access_token)
        response = result.json
        va_account_no = response["data"][0]["account_no"]

        result = self.get_virtual_account(va_account_no, self.access_token)
        response = result.json
        self.assertTrue(response["data"])
        self.assertTrue(response["data"]["account_no"])
        self.assertTrue(response["data"]["va_type"])
        self.assertTrue(response["data"]["name"])
        self.assertTrue(response["data"]["status"])
        self.assertTrue(response["data"]["bank_name"])
        self.assertTrue(response["data"]["trx_id"])

    def test_get_virtual_account_logs(self):
        result = self.get_virtual_accounts(self.access_token)
        response = result.json
        va_account_no = response["data"][0]["account_no"]

        result = self.get_virtual_account_logs(va_account_no, self.access_token)
        response = result.json
        self.assertEqual(response["data"], [])
