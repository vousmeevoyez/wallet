"""
    Test Wallet Services
"""
from unittest.mock import patch, Mock
from app.api import db

from app.test.base import BaseTestCase

from app.api.models import *

from app.api.common.helper import Sms

from app.api.exception.common import SmsError

from app.api.exception.wallet import *

from app.api.wallet.modules.wallet_services import WalletServices
from app.api.wallet.modules.va_services import VirtualAccountServices

class TestWalletServices(BaseTestCase):
    """ Test Class for Wallet Services"""

    def _create_wallet(self):
        wallet = Wallet()
        result = WalletServices.add(self.user, wallet, "123456")
        return result[0]["data"]
    #end def

    def test_add_va(self):
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
        }

        result = VirtualAccountServices.add(virtual_account, params)
        self.assertTrue(result[0]["data"]["virtual_account_id"])
