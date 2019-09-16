"""
    Test Transfer Routes
"""
import uuid
from unittest.mock import Mock, patch

from app.test.base import BaseTestCase

from app.api.models import User
from app.api.models import Wallet
from app.api import db


class TestTransferRoutes(BaseTestCase):
    """ Test Class that represent all test suite for transfer """

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
        TRANSFER 
    """

    def test_transfer(self):
        """ CASE 1 Transfer : successfully transfer """
        # inject balance
        wallet = Wallet.query.get(self._wallet1)
        wallet.balance = 99999999
        db.session.commit()

        params = {
            "amount": "15",
            "notes": "some notes",
            "pin": "123456",
            "types": "PAYROLL",
        }

        result = self.transfer(self._wallet1, self._wallet2, params, self.access_token)
        response = result.get_json()
        self.assertEqual(result.status_code, 202)
        self.assertTrue(response["data"])

    def test_transfer_locked_source(self):
        """ CASE 2 Transfer : but wallet is locked"""
        # lock wallet
        wallet = Wallet.query.get(self._wallet1)
        wallet.lock()
        db.session.commit()

        params = {
            "amount": "15",
            "types": "PAYROLL",
            "notes": "some notes",
            "pin": "123456",
        }

        result = self.transfer(self._wallet1, self._wallet2, params, self.access_token)
        response = result.get_json()
        self.assertEqual(result.status_code, 422)
        self.assertTrue(response["error"], "WALLET_LOCKED")

    def test_transfer_incorrect_pin(self):
        """ CASE 3 Transfer : try transfer with invalid pin"""
        # inject balance
        wallet = Wallet.query.get(self._wallet1)
        wallet.balance = 99999999
        db.session.commit()

        params = {
            "amount": "15",
            "types": "PAYROLL",
            "notes": "some notes",
            "pin": "111111",
        }

        # first attempt
        result = self.transfer(self._wallet1, self._wallet2, params, self.access_token)
        response = result.get_json()

        self.assertEqual(result.status_code, 422)
        self.assertTrue(response["error"], "INCORRECT_PIN")

        # second attempt
        result = self.transfer(self._wallet1, self._wallet2, params, self.access_token)
        response = result.get_json()

        self.assertEqual(result.status_code, 422)
        self.assertTrue(response["error"], "INCORRECT_PIN")

        # third attempt
        result = self.transfer(self._wallet1, self._wallet2, params, self.access_token)
        response = result.get_json()

        self.assertEqual(result.status_code, 422)
        self.assertTrue(response["error"], "INCORRECT_PIN")

        # fourth attempt
        result = self.transfer(self._wallet1, self._wallet2, params, self.access_token)
        response = result.get_json()

        self.assertEqual(result.status_code, 422)
        self.assertTrue(response["error"], "MAX_PIN_ATTEMPT")

        # fifth attempt
        result = self.transfer(self._wallet1, self._wallet2, params, self.access_token)
        response = result.get_json()

        self.assertEqual(result.status_code, 422)
        self.assertTrue(response["error"], "WALLET_LOCKED")

    def test_transfer_invalid_destination(self):
        """ CASE 4 Transfer : try transfer with same between source """
        # inject balance
        wallet = Wallet.query.get(self._wallet1)
        wallet.balance = 99999999
        db.session.commit()

        params = {
            "amount": "15",
            "types": "PAYROLL",
            "notes": "some notes",
            "pin": "123456",
        }

        result = self.transfer(self._wallet1, self._wallet1, params, self.access_token)
        response = result.get_json()
        self.assertEqual(result.status_code, 422)

    """
        BANK TRANSFER 
    """

    def test_bank_transfer(self):
        """ CASE 1 Bank Transfer : successfully bank transfer """
        # inject balance
        wallet = Wallet.query.get(self._wallet1)
        wallet.balance = 99999999
        db.session.commit()

        # add account bank information
        params = {
            "account_no": "3333333333",
            "name": "Bpk KEN AROK",
            "label": "Irene Bank Account",
            "bank_code": "014",
        }
        result = self.create_user_bank_account(self._user1, params, self.access_token)
        response = result.get_json()["data"]

        bank_account_id = response["bank_account_id"]

        params = {"amount": "15", "notes": "some notes", "pin": "123456"}

        result = self.bank_transfer(
            self._wallet1, bank_account_id, params, self.access_token
        )
        self.assertEqual(result.status_code, 202)

    def test_bank_transfer_bank_account_not_found(self):
        """ CASE 2 Bank Transfer invalid bank account id: successfully bank transfer """
        # inject balance
        wallet = Wallet.query.get(self._wallet1)
        wallet.balance = 99999999
        db.session.commit()

        # add account bank information
        params = {
            "account_no": "3333333333",
            "name": "Bpk KEN AROK",
            "label": "Irene Bank Account",
            "bank_code": "014",
        }
        result = self.create_user_bank_account(self._user1, params, self.access_token)
        response = result.get_json()["data"]

        bank_account_id = response["bank_account_id"]

        params = {"amount": "15", "notes": "some notes", "pin": "123456"}
        result = self.bank_transfer(
            self._wallet1, str(uuid.uuid4()), params, self.access_token
        )
        self.assertEqual(result.status_code, 404)

    ############ PATCH #################
    def test_bank_transfer2(self):
        """ CASE 1 Bank Transfer : successfully bank transfer """
        # inject balance
        wallet = Wallet.query.get(self._wallet1)
        wallet.balance = 99999999
        db.session.commit()

        # add account bank information
        params = {
            "account_no": "3333333333",
            "name": "Bpk KEN AROK",
            "label": "Irene Bank Account",
            "bank_code": "014",
        }
        result = self.create_user_bank_account(self._user1, params, self.access_token)
        response = result.get_json()["data"]

        bank_account_id = response["bank_account_id"]

        params = {"amount": "15", "notes": "some notes", "pin": "123456"}

        # api key
        _api_key = "8c574c41-3e01-4763-89af-fd370989da33"

        result = self.bank_transfer2(self._wallet1, bank_account_id, params, _api_key)
        self.assertEqual(result.status_code, 202)
