"""
    Test Wallet Services
"""
from unittest.mock import patch, Mock
from app.api import db

from app.test.base import BaseTestCase

from app.api.models import *

from task.bank.tasks import BankTask

from app.api.wallets.modules.wallet_services import WalletServices
from app.api.virtual_accounts.modules.va_services import VirtualAccountServices
from app.api.const import STATUS


class TestVaServices(BaseTestCase):
    """ Test Class for Wallet Services"""

    def _create_wallet(self):
        wallet = Wallet()
        result = WalletServices().add(self.user, wallet, "123456")
        return result[0]["data"]

    # end def

    def _create_va(self):
        va_credit = VaType(key="CREDIT")

        db.session.add(va_credit)
        db.session.commit()

        # create bank here
        bank = Bank(key="BNI", name="Bank BNI", code="009")
        db.session.add(bank)
        db.session.commit()

        # create virtual account credit
        va = VirtualAccount(
            amount="100", name="Lisa", va_type_id=va_credit.id,
            bank_id=bank.id, status=STATUS["ACTIVE"]
        )
        va.generate_va_number()
        va.generate_trx_id()
        va.get_datetime_expired("BNI", "CREDIT")
        db.session.add(va)
        db.session.commit()
        return va

    @patch.object(BankTask, "create_va")
    def test_add_va(self, mock_create_va):
        """ test method for creating va"""
        response = self._create_wallet()

        wallet_id = response["wallet_id"]

        virtual_account = VirtualAccount(name="lisa")

        params = {
            "bank_name": "BNI",
            "type": "CREDIT",
            "wallet_id": wallet_id,
            "amount": 0,
        }

        mock_create_va.return_value = True
        result = VirtualAccountServices().add(virtual_account, params)
        self.assertTrue(result[0]["data"]["virtual_account"])

    @patch.object(BankTask, "create_va")
    def test_info_va(self, mock_create_va):
        """ test method for returning va information """
        response = self._create_wallet()

        wallet_id = response["wallet_id"]

        virtual_account = VirtualAccount(name="lisa")

        params = {
            "bank_name": "BNI",
            "type": "CREDIT",
            "wallet_id": wallet_id,
            "amount": 0,
        }

        mock_create_va.return_value = True
        result = VirtualAccountServices().add(virtual_account, params)
        virtual_account = result[0]["data"]["virtual_account"]

        result = VirtualAccountServices(virtual_account).info()
        self.assertTrue(result["data"])


    @patch.object(BankTask, "create_va")
    def test_show(self, mock_create_va):
        """ test method for showing all va"""
        response = self._create_wallet()

        wallet_id = response["wallet_id"]

        virtual_account = VirtualAccount(name="lisa")

        params = {
            "bank_name": "BNI",
            "type": "CREDIT",
            "wallet_id": wallet_id,
            "amount": 0,
        }

        mock_create_va.return_value = True
        result = VirtualAccountServices().add(virtual_account, params)
        self.assertTrue(result[0]["data"]["virtual_account"])

        result = VirtualAccountServices().show()
        self.assertEqual(len(result), 2)

    def test_get_logs(self):
        """ test method for showing all va logs """
        va = self._create_va()

        # create dummy logs for testing!
        va_log = VaLog(
            virtual_account_id=va.id, balance=1000
        )

        va_log2 = VaLog(
            virtual_account_id=va.id, balance=1100
        )

        va_log3 = VaLog(
            virtual_account_id=va.id, balance=1200
        )

        db.session.add(va_log)
        db.session.add(va_log2)
        db.session.add(va_log3)
        db.session.commit()

        result = VirtualAccountServices(virtual_account_no=va.account_no).get_logs()
        data = result[0]["data"]
        # make sure it return a right data
        self.assertEqual(len(data), 3)
        # have 2 balance and created at
        self.assertTrue(data[0]["balance"])
        self.assertTrue(data[0]["created_at"])
