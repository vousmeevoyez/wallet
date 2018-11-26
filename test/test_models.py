import sys
import json
import unittest

sys.path.append("../")
sys.path.append("../app")

from datetime import datetime, timedelta

from app            import create_app, db
from app.models     import ApiKey, Wallet, VirtualAccount, Transaction, ExternalLog, User, BlacklistToken
from app.config     import config

now = datetime.utcnow()

class TestConfig(config.Config):
    TESTING = True
    #SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SQLALCHEMY_DATABASE_URI = 'postgresql://modana:password@localhost/unittest_db'

class ApiKeyModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_generate_access_key(self):
        key = ApiKey(label='SAMPLELABLE', name='SAMPLENAME')
        key.generate_access_key(20)
        self.assertEqual(len(key.access_key), 2*20)

        key = ApiKey(label='SAMPLELABLE', name='SAMPLENAME')
        key.generate_access_key(10)
        self.assertEqual(len(key.access_key), 2*10)

    def test_set_expiration(self):
        key = ApiKey(label='SAMPLELABLE', name='SAMPLENAME')
        key.set_expiration(525600)
        self.assertEqual(key.expiration.replace(microsecond=0),  (now + timedelta(minutes=525600)).replace(microsecond=0) )

        key = ApiKey(label='SAMPLELABLE', name='SAMPLENAME')
        key.set_expiration(43800)
        self.assertEqual(key.expiration.replace(microsecond=0),  (now + timedelta(minutes=43800)).replace(microsecond=0) )

    def test_revoke_access_key(self):
        key = ApiKey(label='SAMPLELABLE', name='SAMPLENAME')
        key.set_expiration(525600)
        key.revoke_access_key()

        key2 = ApiKey(label='SAMPLELABLE2', name='SAMPLENAME2')
        key2.set_expiration(43800)
        key2.revoke_access_key()

        self.assertEqual(key.expiration.hour,  (now + timedelta(seconds=1)).hour)
        self.assertEqual(key2.expiration.minute,  (now + timedelta(seconds=1)).minute )

    def test_check_access_key(self):
        key = ApiKey(label='SAMPLELALE3', name='SAPLENAME3')
        key.generate_access_key(20)
        key.set_expiration(525600)

        self.assertEqual(len(key.access_key), 40)

    def test_password(self):
        key = ApiKey(label='SAMPLELABLE4', name='SAMPLENAME4')
        key.generate_access_key(20)
        key.set_expiration(525600)
        key.set_password("password")
        db.session.add(key)
        db.session.commit()

        key = ApiKey.query.get(1)
        self.assertTrue(key.check_password("password"))
        self.assertFalse(key.check_password("test"))

class UserTestCaseModel(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_wallet_relation(self):
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            msisdn='081219644314',
        )
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        wallet = Wallet(
            user_id = user.id,
        )
        db.session.add(wallet)
        db.session.commit()

        user = User.query.get(1)
        self.assertEqual( len(user.wallets), 1)

    def test_password(self):
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            msisdn='081219644314',
        )
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        user = User.query.get(1)
        self.assertTrue(user.check_password("password"))
        self.assertFalse(user.check_password("test"))

class WalletModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_check_balance(self):
        wallet = Wallet(
        )
        db.session.add(wallet)
        db.session.commit()

        user = Wallet.query.get(1)
        balance = user.check_balance()
        self.assertEqual( balance, 0)

    def test_add_balance(self):
        wallet = Wallet(
        )

        db.session.add(wallet)
        db.session.commit()

        user = Wallet.query.get(1)
        user.add_balance(1000)
        user.add_balance(1000)
        user.add_balance(1000)
        user.add_balance(1000)
        user.add_balance(1000)

        balance = user.check_balance()
        self.assertEqual( balance, 5000)

    def test_deduct_balance(self):
        wallet = Wallet(
        )
        db.session.add(wallet)
        db.session.commit()

        user = Wallet.query.get(1)
        user.add_balance(1000)
        user.deduct_balance(999)

        balance = user.check_balance()
        self.assertEqual( balance, 1)

    def test_check_lock(self):
        wallet = Wallet(
        )
        db.session.add(wallet)
        db.session.commit()

        user = Wallet.query.get(1)
        lock_status = user.is_unlocked()

        self.assertEqual( lock_status, True)

    def test_lock(self):
        wallet = Wallet(
        )
        db.session.add(wallet)
        db.session.commit()

        user = Wallet.query.get(1)
        user.lock()
        db.session.commit()
        lock_status = user.is_unlocked()

        self.assertEqual( lock_status, False)


    def test_unlock(self):
        wallet = Wallet(
        )
        db.session.add(wallet)
        db.session.commit()

        user = Wallet.query.get(1)
        user.lock()
        db.session.commit()
        user.unlock()
        db.session.commit()
        lock_status = user.is_unlocked()

        self.assertEqual( lock_status, True)

    def test_pin(self):
        wallet = Wallet(
        )
        wallet.set_pin("123456")
        self.assertTrue( wallet.check_pin("123456") )
        self.assertFalse( wallet.check_pin("123654") )

    def test_generate_wallet_id(self):
        wallet_id = Wallet().generate_wallet_id()
        self.assertEqual( len(wallet_id), 10)

    def test_va_relationship(self):
        wallet = Wallet(
        )
        db.session.add(wallet)
        db.session.commit()

        wallet = Wallet.query.get(1)
        va = VirtualAccount(
            trx_amount="100",
            name="Lisa",
            wallet_id=wallet.id,
            bank_id=1,
            va_type=1
        )
        va_id  = va.generate_va_number("CREDIT")
        trx_id = va.generate_trx_id()
        db.session.add(va)
        db.session.commit()

        va = VirtualAccount(
            trx_amount="101",
            name="Lisa",
            wallet_id=wallet.id,
            bank_id=1,
            va_type=2
        )
        va_id  = va.generate_va_number("CREDIT")
        trx_id = va.generate_trx_id()

        db.session.add(va)
        db.session.commit()

        self.assertEqual(len(wallet.virtual_accounts), 2)

    def test_is_owned(self):
        user = User(
            username='lisabp',
            name='lisa',
            email='lisa@bp.com',
            msisdn='081219644314',
        )
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

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

class VirtualAccountModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_generate_va_number(self):
        va_number = VirtualAccount().generate_va_number("CREDIT")
        self.assertEqual(len(va_number), 16)

        va_number = VirtualAccount().generate_va_number("CARDLESS")
        self.assertEqual(len(va_number), 16)

    def test_inject_balance(self):
        wallet = Wallet(
        )
        db.session.add(wallet)
        db.session.commit()

        va_source = 123456
        wallet_id = 1
        amount    = 100

        inject_status = VirtualAccount().inject_balance(va_source, wallet_id, amount)
        self.assertTrue(inject_status)

        user = Wallet.query.get(1)
        balance = user.check_balance()
        self.assertEqual( balance, amount)

        print(Transaction.query.all())

class TransactionModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

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

class ExternalModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

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

class BlacklistTokenModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_is_blacklisted(self):
        token = BlacklistToken(token="adsjkdsjlkjdsljdsl")
        db.session.add(token)
        db.session.commit()

        result = BlacklistToken.is_blacklisted("adsjkdsjlkjdsljdsl")
        self.assertTrue(result)

if __name__ == "__main__":
    unittest.main(verbosity=2)
