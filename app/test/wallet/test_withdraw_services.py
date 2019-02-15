"""
    Test Withdraw Services
"""
from unittest.mock import patch, Mock
from app.api import db

from app.test.base  import BaseTestCase

from app.api.models import *

from task.bank.tasks import BankTask

from app.api.wallet.modules.withdraw_services import WithdrawServices
from app.api.wallet.modules.va_services import VirtualAccountServices
from app.api.wallet.modules.wallet_services import WalletServices
# exceptions
from app.api.error.http import *

class TestWithdrawServices(BaseTestCase):
    """ Test Class for Withdraw Services"""

    @patch.object(BankTask, "create_va")
    def _create_wallet_with_va(self, mock_create_va):
        wallet = Wallet()
        result = WalletServices.add(self.user, wallet, "123456")
        response = result[0]["data"]
        wallet_id = response["wallet_id"]

        virtual_account = VirtualAccount(
            name="lisa",
        )

        params = {
            "bank_name" : "BNI",
            "type"      : "DEBIT",
            "wallet_id" : wallet_id,
            "amount"    : "10000000"
        }

        mock_create_va.return_value = True
        result = VirtualAccountServices.add(virtual_account, params)
        self.assertTrue(result[0]["data"]["virtual_account"])
        
        wallet = Wallet.query.filter_by(id=wallet_id).first()
        return wallet

    @patch.object(BankTask, "create_va")
    def _create_wallet_without_va(self, mock_create_va):
        wallet = Wallet()
        result = WalletServices.add(self.user, wallet, "123456")
        response = result[0]["data"]
        wallet_id = response["wallet_id"]

        virtual_account = VirtualAccount(
            name="lisa",
        )

        wallet = Wallet.query.filter_by(id=wallet_id).first()
        return wallet

    def test_request_withdraw_success(self):
        """ test function to request withdraw """
        source = self._create_wallet_without_va()
        source.balance = 500000

        params = {
            "amount"    : 50000,
            "bank_name" : "BNI",
        }

        result = WithdrawServices(source.id, "123456").request(params)
        print(result)

    def test_request_withdraw_pending(self):
        """ test function to request withdraw """
        source = self._create_wallet_without_va()
        source.balance = 500000

        params = {
            "amount"    : 50000,
            "bank_name" : "BNI",
        }

        result = WithdrawServices(source.id, "123456").request(params)

        with self.assertRaises(UnprocessableEntity):
            result = WithdrawServices(source.id, "123456").request(params)

    def test_request_withdraw_va_already_exist(self):
        """ test function to request withdraw """
        source = self._create_wallet_with_va()
        source.balance = 500000

        params = {
            "amount"    : 50000,
            "bank_name" : "BNI",
        }

        result = WithdrawServices(source.id, "123456").request(params)
        print(result)

    def test_request_withdraw_minimal(self):
        """ test function to request withdraw """
        source = self._create_wallet_without_va()

        params = {
            "amount"    : 1000,
            "bank_name" : "BNI"
        }

        with self.assertRaises(UnprocessableEntity):
            result = WithdrawServices(source.id, "123456").request(params)

    def test_request_withdraw_max(self):
        """ test function to request withdraw """
        source = self._create_wallet_without_va()

        params = {
            "amount"    : 99999999999999999999,
            "bank_name" : "BNI"
        }

        with self.assertRaises(UnprocessableEntity):
            result = WithdrawServices(source.id, "123456").request(params)

    def test_request_withdraw_insufficient(self):
        """ test function to request withdraw """
        source = self._create_wallet_without_va()

        params = {
            "amount" : 99999,
            "bank_name" : "BNI"
        }

        with self.assertRaises(UnprocessableEntity):
            result = WithdrawServices(source.id, "123456").request(params)

    def test_request_withdraw_incorrect_pin(self):
        """ test function to request withdraw """
        source = self._create_wallet_without_va()
        source.balance = 1000

        params = {
            "amount" : 99999,
            "bank_name" : "BNI"
        }

        with self.assertRaises(UnprocessableEntity):
            result = WithdrawServices(source.id, "111111").request(params)
