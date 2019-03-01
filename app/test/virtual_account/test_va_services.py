"""
    Test Wallet Services
"""
from unittest.mock import patch, Mock
from app.api import db

from app.test.base import BaseTestCase

from app.api.models import *

from task.bank.tasks import BankTask

from app.api.wallet.modules.wallet_services import WalletServices
from app.api.virtual_account.modules.va_services import VirtualAccountServices

class TestVaServices(BaseTestCase):
    """ Test Class for Wallet Services"""

    def _create_wallet(self):
        wallet = Wallet()
        result = WalletServices.add(self.user, wallet, "123456")
        return result[0]["data"]
    #end def

    @patch.object(BankTask, "create_va")
    def test_add_va(self, mock_create_va):
        """ test method for creating va"""
        response = self._create_wallet()

        wallet_id = response["wallet_id"]

        virtual_account = VirtualAccount(
            name="lisa",
        )

        params = {
            "bank_name" : "BNI",
            "type"      : "CREDIT",
            "wallet_id" : wallet_id,
            "amount"    : 0
        }

        mock_create_va.return_value = True
        result = VirtualAccountServices.add(virtual_account, params)
        self.assertTrue(result[0]["data"]["virtual_account"])

    @patch.object(BankTask, "create_va")
    def test_info_va(self, mock_create_va):
        """ test method for returning va information """
        response = self._create_wallet()

        wallet_id = response["wallet_id"]

        virtual_account = VirtualAccount(
            name="lisa",
        )

        params = {
            "bank_name" : "BNI",
            "type"      : "CREDIT",
            "wallet_id" : wallet_id,
            "amount"    : 0
        }

        mock_create_va.return_value = True
        result = VirtualAccountServices.add(virtual_account, params)
        virtual_account = result[0]["data"]["virtual_account"]

        result = VirtualAccountServices(virtual_account).info()
        self.assertTrue(result["data"])

    @patch.object(BankTask, "create_va")
    def test_update_va(self, mock_create_va):
        """ test method for creating va"""
        response = self._create_wallet()

        wallet_id = response["wallet_id"]

        virtual_account = VirtualAccount(
            name="lisa",
        )

        params = {
            "bank_name" : "BNI",
            "type"      : "CREDIT",
            "wallet_id" : wallet_id,
            "amount"    : 0
        }

        mock_create_va.return_value = True
        result = VirtualAccountServices.add(virtual_account, params)
        self.assertTrue(result[0]["data"]["virtual_account"])

        virtual_account = result[0]["data"]["virtual_account"]

        params = {
            "bank_name" : "BNI",
            "type"      : "CREDIT",
            "amount"    : "1111111",
        }

        result = VirtualAccountServices(virtual_account).update(params)
        self.assertTrue(result["virtual_account"])
        self.assertTrue(result["valid_until"])

