"""
    Test Withdraw Services
"""
from unittest.mock import patch, Mock
from app.api import db

from app.test.base  import BaseTestCase

from app.api.models import Payment
from app.api.models import Wallet
from app.api.models import Transaction
from app.api.models import MasterTransaction
from app.api.models import Bank
from app.api.models import BankAccount

from app.api.wallet.modules.withdraw_services import WithdrawServices

# exceptions
from app.api.exception.wallet import *

from app.api.exception.bank import BankAccountNotFoundError

class TestWithdrawServices(BaseTestCase):
    """ Test Class for Withdraw Services"""

    def _create_source_destination(self):
        source_wallet = Wallet(user_id=self.user.id)
        source_wallet.set_pin("123456")
        db.session.add(source_wallet)
        db.session.commit()

        source_wallet.add_balance(1000)
        db.session.flush()

        # create destination wallet secondly
        destination_wallet = Wallet()
        destination_wallet.set_pin("123456")
        db.session.add(destination_wallet)
        db.session.commit()

        return source_wallet, destination_wallet

    def test_request_withdraw_success(self):
        """ test function to request withdraw """
        source, destination = self._create_source_destination()
        source.balance = 500000

        params = {
            "amount" : 50000,
        }

        result = WithdrawServices(source.id, "123456").request(params)
        print(result)

    def test_request_withdraw_minimal(self):
        """ test function to request withdraw """
        source, destination = self._create_source_destination()

        params = {
            "amount" : 1000,
        }

        with self.assertRaises(MinimalWithdrawError):
            result = WithdrawServices(source.id, "123456").request(params)

    def test_request_withdraw_max(self):
        """ test function to request withdraw """
        source, destination = self._create_source_destination()

        params = {
            "amount" : 99999999999999999999,
        }

        with self.assertRaises(MaxWithdrawError):
            result = WithdrawServices(source.id, "123456").request(params)

    def test_request_withdraw_insufficient(self):
        """ test function to request withdraw """
        source, destination = self._create_source_destination()

        params = {
            "amount" : 99999,
        }

        with self.assertRaises(InsufficientBalanceError):
            result = WithdrawServices(source.id, "123456").request(params)

    def test_request_withdraw_insufficient(self):
        """ test function to request withdraw """
        source, destination = self._create_source_destination()
        source.balance = 500000

        params = {
            "amount" : 99999,
        }

        result = WithdrawServices(source.id, "123456").request(params)

        params = {
            "amount" : 99999,
        }

        with self.assertRaises(RaisePendingWithdrawError):
            result = WithdrawServices(source.id, "123456").request(params)
