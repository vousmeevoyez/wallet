""" 
    Bank Handler Test
"""
import unittest

from unittest.mock import Mock, patch
from datetime import datetime

from app.test.base        import BaseTestCase
from app.api              import db
from app.api.bank.handler import BankHandler
from app.api.bank.bni.helper import BNI
from app.api.models       import *

class TestBankHandler(BaseTestCase):
    """ Test Bank Handler Class"""

    def test_get_datetime_expired(self):
        """ test function to generate datetime expired based on which bank and
        what kind of va type"""
        result = BankHandler("BNI")._get_datetime_expired("CREDIT")
        self.assertIsInstance(result, datetime)

    def test_bank_name_to_id(self):
        """ test function to convert bank name to bank id"""
        result = BankHandler._bank_name_to_id("BNI")
        self.assertIsInstance(result, int)

    def test_create_va_success(self):
        """ test function to create va record"""
        wallet = Wallet()
        db.session.add(wallet)
        db.session.commit()

        params = {
            "wallet_id" : wallet.id,
            "type"      : "CREDIT",
            "name"      : "Jennie",
        }
        result = BankHandler("BNI")._create_va(params)
        self.assertEqual(result["status"], "SUCCESS")

        test = VirtualAccount.query.all()
        print(test)

    def test_create_va_already_exist_failed(self):
        """ test function to create va record"""

        wallet = Wallet()
        db.session.add(wallet)
        db.session.commit()

        params = {
            "wallet_id" : wallet.id,
            "type"      : "CREDIT",
            "name"      : "Jennie",
        }
        result = BankHandler("BNI")._create_va(params)
        self.assertEqual(result["status"], "SUCCESS")

        result = BankHandler("BNI")._create_va(params)
        self.assertEqual(result["status"], "FAILED")

    @patch.object(BNI, 'call')
    def test_dispatch_create_va(self, mock_function):
        """ test dispatch function to create va"""
        wallet = Wallet()
        db.session.add(wallet)
        db.session.commit()

        params = {
            "wallet_id" : wallet.id,
            "amount"    : 0,
            "name"      : "Kelvin",
            "msisdn"    : "6281219644314",
            "type"      : "CREDIT",
        }
        mock_function.return_value = { 
            "status" : "SUCCESS",
            "data"   : "some va data",
        }
        result = BankHandler("BNI").dispatch("CREATE_VA", params)
        self.assertEqual(result["status"], "SUCCESS")

    @patch.object(BNI, 'call')
    def test_dispatch_create_cardless_va(self, mock_function):
        """ test dispatch function to create va"""
        wallet = Wallet()
        db.session.add(wallet)
        db.session.commit()

        params = {
            "wallet_id" : wallet.id,
            "amount"    : 0,
            "name"      : "Kelvin",
            "msisdn"    : "6281219644314",
            "type"      : "DEBIT", # BNI DEBIT MEAN CARDLESS
        }
        mock_function.return_value = {
            "status" : "SUCCESS",
            "data"   : "some va data",
        }
        result = BankHandler("BNI").dispatch("CREATE_VA", params)
        self.assertEqual(result["status"], "SUCCESS")

    @patch.object(BNI, 'call')
    def test_dispatch_transfer(self, mock_function):
        """ test dispatch function to create va"""
        wallet = Wallet()
        db.session.add(wallet)
        db.session.commit()

        params = {
            "source_account" : "123456", # master account no
            "account_no" : "11111111111", # destination bank account no
            "account_name" : "Jennie", # destination bank account name
            "bank_code" : "123", # destination bank code
            "bank_name" : "BCA", # destination bank code
            "amount" : 1,
            "transfer_ref" : "1238392832",
        }
        mock_function.return_value = {
            "status" : "SUCCESS",
            "data"   : "some va data",
        }
        result = BankHandler("BNI").dispatch("DIRECT_TRANSFER", params)
        self.assertEqual(result["status"], "SUCCESS")
