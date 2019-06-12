"""
    Integration Testing between wallet & routes
"""
import json
from unittest.mock import Mock, patch

from app.test.base import BaseTestCase

from app.api.models import *
from app.api import db

from task.bank.BNI.utility import remote_call

from app.config import config

BNI_ECOLLECTION_CONFIG = config.Config.BNI_ECOLLECTION_CONFIG

class TestCallbackRoutes(BaseTestCase):
    """ Test Class for Wallet Routes"""
    def setUp(self):
        super().setUp()

        user_id, wallet_id = self.create_dummy_user(self.access_token)
        self.user_id = user_id
        self.wallet_id = wallet_id
    #end def

    """
        DEPOSIT CALLBACK
    """
    def test_deposit_callback(self):
        """ DEPOSIT CALLBACK CASE 1 : Successfully deposit callback """
        params = {
            "user_id" : self.user_id,
            "access_token" : self.access_token,
            "label" : "wallet label",
            "pin" : "123456"
        }

        result = self.create_wallet(params, self.access_token)
        response = result.get_json()
        self.assertEqual(result.status_code, 201)

        user = User.query.filter_by(id=params["user_id"]).first()

        data = {
            "virtual_account"           :
            user.wallets[0].virtual_accounts[0].account_no,
            "customer_name"             : "jennie",
            "trx_id"                    : user.wallets[0].virtual_accounts[0].trx_id,
            "trx_amount"                : "0",
            "payment_amount"            : "50000",
            "cumulative_payment_amount" : "50000",
            "payment_ntb"               : "12345",
            "datetime_payment"          : "2018-12-20 11:16:00",
        }
        encrypted_data = remote_call.encrypt(BNI_ECOLLECTION_CONFIG["CREDIT_CLIENT_ID"], BNI_ECOLLECTION_CONFIG["CREDIT_SECRET_KEY"], data)

        expected_value = {
            "client_id" : BNI_ECOLLECTION_CONFIG["CREDIT_CLIENT_ID"],
            "data"      : encrypted_data.decode("UTF-8")
        }
        result = self.deposit_callback(expected_value)
        response = result.get_json()
        self.assertEqual(response["status"], "000")

        transaction = Transaction.query.all()
        print(transaction)

    """
        WITHDRAW CALLBACK
    """
    def test_withdraw_callback(self):
        """ WITHDRAW CALLBACK CASE 1 : Successfully withdraw callback """
        params = {
            "user_id" : self.user_id,
            "access_token" : self.access_token,
            "label" : "wallet label",
            "pin" : "123456"
        }

        result = self.create_wallet(params, self.access_token)
        response = result.get_json()
        self.assertEqual(result.status_code, 201)

        user = User.query.filter_by(id=params["user_id"]).first()

        data = {
            "virtual_account"           :
            user.wallets[0].virtual_accounts[0].account_no,
            "customer_name"             : "jennie",
            "trx_id"                    : user.wallets[0].virtual_accounts[0].trx_id,
            "trx_amount"                : "0",
            "payment_amount"            : "-50000",
            "cumulative_payment_amount" : "-50000",
            "payment_ntb"               : "12345",
            "datetime_payment"          : "2018-12-20 11:16:00",
        }
        encrypted_data = \
        remote_call.encrypt(BNI_ECOLLECTION_CONFIG["DEBIT_CLIENT_ID"],
                            BNI_ECOLLECTION_CONFIG["DEBIT_SECRET_KEY"], data)

        expected_value = {
            "client_id" : BNI_ECOLLECTION_CONFIG["DEBIT_CLIENT_ID"],
            "data"      : encrypted_data.decode("UTF-8")
        }
        result = self.withdraw_callback(expected_value)
        response = result.get_json()
        self.assertEqual(response["status"], "000")

        transaction = Transaction.query.all()
        print(transaction)
