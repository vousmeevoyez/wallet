import sys
import json
import unittest

from datetime import datetime, timedelta

from app.test.base  import BaseTestCase
from app.api        import db
from app.api.models import *
from app.api.config import config

now = datetime.utcnow()

class UserTestCaseModel(BaseTestCase):
    def test_user_role_relation(self):
        # create user role first
        role = Role(
            description="USER",
        )
        db.session.add(role)
        db.session.commit()

        # create dummy user
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            phone_ext='62',
            phone_number='81219644314',
            role_id=role.id,
        )
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        # create dummy user
        user2 = User(
            username='jenniebp',
            name='jennie',
            email='jennie@bp.com',
            phone_ext='62',
            phone_number='82219644314',
            role_id=role.id,
        )
        user2.set_password("password")
        db.session.add(user2)
        db.session.commit()

        # get user by their role
        self.assertEqual( len(role.user), 2)

    def test_wallet_relation(self):
        # create dummy user
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            phone_ext='62',
            phone_number='81219644314',
        )
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        # create dummy wallet and link it to the user
        wallet = Wallet(
            user_id = user.id,
        )
        db.session.add(wallet)
        db.session.commit()

        user = User.query.get(1)
        # check how many wallet user have
        self.assertEqual( len(user.wallets), 1)

    def test_password(self):
        # create dummy user
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            phone_ext='62',
            phone_number='81219644314',
        )
        # set password
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        # fetch user
        user = User.query.get(1)
        # check password here
        self.assertTrue(user.check_password("password"))
        self.assertFalse(user.check_password("test"))

class WalletModelCase(BaseTestCase):

    def test_check_balance(self):
        # create dummy wallet
        wallet = Wallet(
        )
        db.session.add(wallet)
        db.session.commit()

        # fetch user object
        user = Wallet.query.get(1)

        # check balance 
        balance = user.check_balance()
        self.assertEqual( balance, 0)

    def test_add_balance(self):
        # create dummy wallet
        wallet = Wallet(
        )

        db.session.add(wallet)
        db.session.commit()

        # fetch wallet
        user = Wallet.query.get(1)
        # add balance here
        user.add_balance(1000)
        user.add_balance(1000)
        user.add_balance(1000)
        user.add_balance(1000)
        user.add_balance(1000)

        # check balance here
        balance = user.check_balance()
        self.assertEqual( balance, 5000)

    def test_deduct_balance(self):
        # create dummy wallet
        wallet = Wallet(
        )
        db.session.add(wallet)
        db.session.commit()

        # fetch user wallet
        wallet = Wallet.query.get(1)
        wallet.add_balance(1000)
        wallet.deduct_balance(999)

        # check balance and make sure the amount is correct
        balance = wallet.check_balance()
        self.assertEqual( balance, 1)

    def test_check_lock(self):
        # create dummy wallet
        wallet = Wallet(
        )
        db.session.add(wallet)
        db.session.commit()

        # fetch user wallet
        wallet = Wallet.query.get(1)
        lock_status = wallet.is_unlocked()

        # check wallet status
        self.assertEqual( lock_status, True)

    def test_lock(self):
        # create dummy wallet
        wallet = Wallet(
        )
        db.session.add(wallet)
        db.session.commit()

        # fetch user wallet
        wallet= Wallet.query.get(1)
        wallet.lock()
        db.session.commit()

        # check lock here
        lock_status = wallet.is_unlocked()
        self.assertEqual( lock_status, False)

    def test_unlock(self):
        # create dummy wallet
        wallet = Wallet(
        )
        db.session.add(wallet)
        db.session.commit()

        # fetch user wallet
        wallet = Wallet.query.get(1)
        wallet.lock()
        db.session.commit()

        # unlock here
        wallet.unlock()
        db.session.commit()
        lock_status = wallet.is_unlocked()

        # make sure the wallet is unlocked
        self.assertEqual( lock_status, True)

    def test_pin(self):
        # create dummy wallet here
        wallet = Wallet(
        )
        # set pin
        wallet.set_pin("123456")
        # check pin
        self.assertTrue( wallet.check_pin("123456") )
        self.assertFalse( wallet.check_pin("123654") )

    def test_generate_wallet_id(self):
        wallet_id = Wallet().generate_wallet_id()
        self.assertEqual( len(wallet_id), 10)

    def test_va_relationship(self):
        # create dummy wallet here
        wallet = Wallet(
        )
        db.session.add(wallet)
        db.session.commit()

        # fetch wallet here
        wallet = Wallet.query.get(1)

        # create bank here
        bni = Bank(
            key="BNI"
        )
        db.session.add(bni)
        db.session.commit()

        # create virtual_account_type here
        # credit
        va_credit = VaType(
            key="CREDIT"
        )

        # debit
        va_debit = VaType(
            key="DEBIT"
        )
        db.session.add(va_debit)
        db.session.add(va_credit)
        db.session.commit()

        # create virtual account credit
        va = VirtualAccount(
            trx_amount="100",
            name="Lisa",
            wallet_id=wallet.id,
            bank_id=bni.id,
            va_type_id=va_credit.id
        )
        va_id  = va.generate_va_number()
        trx_id = va.generate_trx_id()
        db.session.add(va)
        db.session.commit()

        # create virtual account debit
        va = VirtualAccount(
            trx_amount="101",
            name="Lisa",
            wallet_id=wallet.id,
            bank_id=bni.id,
            va_type_id=va_debit.id
        )
        va_id  = va.generate_va_number()
        trx_id = va.generate_trx_id()

        db.session.add(va)
        db.session.commit()

        # make sure 2 virtual account is associated with wallet
        self.assertEqual(len(wallet.virtual_accounts), 2)

        # make sure each virtual acount type is associate with virtual account
        self.assertEqual(len(va_credit.virtual_account), 1)
        self.assertEqual(len(va_debit.virtual_account), 1)

        # make sure each bank is associated with virtual_account
        self.assertEqual(len(bni.virtual_account), 2)

    def test_is_owned(self):
        # create dummy user here
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            phone_ext='62',
            phone_number='81219644314',
        )
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        # create user wallet here
        wallet = Wallet(
            user_id = user.id,
        )
        wallet_id = wallet.generate_wallet_id()
        db.session.add(wallet)
        db.session.commit()

        result = Wallet.is_owned(1, wallet_id)
        self.assertTrue(result)

        result = Wallet.is_owned(1, 456464)
        self.assertFalse(result)

class VirtualAccountModelCase(BaseTestCase):

    def test_generate_va_number(self):
        # create virtual_account_type here
        # credit
        va_credit = VaType(
            key="CREDIT"
        )

        # debit
        va_debit = VaType(
            key="DEBIT"
        )
        db.session.add(va_debit)
        db.session.add(va_credit)
        db.session.commit()

        # create virtual account credit
        va = VirtualAccount(
            trx_amount="100",
            name="Lisa",
            va_type_id=va_credit.id
        )
        va_id  = va.generate_va_number()
        trx_id = va.generate_trx_id()
        db.session.add(va)
        db.session.commit()

        va_number = va.generate_va_number()
        self.assertEqual(len(va_number), 16)

class TransactionModelCase(BaseTestCase):
    def test_debit_transaction(self):
        wallet = Wallet(
        )
        wallet2 = Wallet(
        )

        db.session.add(wallet)
        db.session.add(wallet2)
        db.session.commit()

        user = Wallet.query.get(1)
        user.add_balance(1000)
        db.session.commit()

        user = Wallet.query.get(1)
        self.assertEqual(user.check_balance(), 1000)

        user2 = Wallet.query.get(2)
        user2.add_balance(1000)
        db.session.commit()

        user2 = Wallet.query.get(2)
        self.assertEqual(user2.check_balance(), 1000)

        #create transaction here
        #(-) deduct balance first
        debit_trx = Transaction(
            source_id = user.id,
            destination_id = user2.id,
            amount = 100,
            transaction_type= True,
            notes="this is debit trx"
        )
        debit_trx.generate_trx_id()
        user.deduct_balance(100)

        credit_trx = Transaction(
            source_id = user2.id,
            destination_id = user.id,
            amount = 100,
            transaction_type= False,
            notes="this is credit trx"
        )
        credit_trx.generate_trx_id()
        user2.add_balance(100)

        db.session.add(debit_trx)
        db.session.add(credit_trx)
        db.session.commit()

        user2 = Wallet.query.get(2)
        self.assertEqual(user2.check_balance(), 1100)

        user = Wallet.query.get(1)
        self.assertEqual(user.check_balance(), 900)

class ExternalModelCase(BaseTestCase):

    def test_set_status(self):
        request  = { "client_id" : 123, "payload" : "this is my payload"}
        response = { "client_id" : 123, "payload" : "this is my payload"}

        log = ExternalLog(
            id = 1,
            status = True,
            request = request,
            response= response,
        )
        log.set_status(True)

        log2 = ExternalLog(
            id = 2,
            status = True,
            request = request,
            response= response,
        )
        log2.set_status(False)
        db.session.add(log)
        db.session.add(log2)
        db.session.commit()

        result  = ExternalLog.query.get(1)
        result2 = ExternalLog.query.get(2)

        self.assertTrue(result.status)
        self.assertFalse(result2.status)

class ForgotPinModelCase(BaseTestCase):
    def test_set_otp_code(self):
        # create wallet
        wallet = Wallet(
        )
        db.session.add(wallet)
        db.session.commit()

        wallet = Wallet.query.get(1)

        # create forgot pin record
        forgot_pin = ForgotPin(
            wallet_id=wallet.id
        )
        forgot_pin.set_otp_code("123456")
        db.session.add(forgot_pin)
        db.session.commit()

    def test_check_otp_code(self):
        # create wallet
        wallet = Wallet(
        )
        db.session.add(wallet)
        db.session.commit()

        wallet = Wallet.query.get(1)

        # create forgot pin record
        forgot_pin = ForgotPin(
            wallet_id=wallet.id
        )
        forgot_pin.set_otp_code("123456")
        db.session.add(forgot_pin)
        db.session.commit()

        forgot_pin = ForgotPin.query.get(1)
        result = forgot_pin.check_otp_code("123456")

        self.assertTrue(result)

class BankAccountModelCase(BaseTestCase):

    def test_relation_bank_account(self):
        role = Role(
            description="USER",
        )
        db.session.add(role)
        db.session.commit()

        # create dummy user
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            phone_ext='62',
            phone_number='81219644314',
            role_id=role.id,
        )
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        # create bank here
        bni=Bank(
            key="BNI",
            name="Bank BNI",
            code="99",
        )
        db.session.add(bni)
        db.session.commit()

        # create bank account here
        bank_account = BankAccount(
            name="Lisa",
            bank_id=bni.id,
            user_id=user.id
        )
        db.session.add(bank_account)
        db.session.commit()

        # create another bank here
        bca=Bank(
            key="BCA",
            name="Bank BCA",
            code="100",
        )
        db.session.add(bca)
        db.session.commit()

        # create bank account here
        bank_account = BankAccount(
            name="Lisa",
            bank_id=bca.id,
            user_id=user.id
        )
        db.session.add(bank_account)
        db.session.commit()

        # make sure user is associated to bank account
        print(user.bank_accounts)
        self.assertEqual( len(user.bank_accounts), 2)

if __name__ == "__main__":
    unittest.main(verbosity=2)
