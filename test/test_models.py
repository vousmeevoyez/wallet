import sys
import unittest

sys.path.append("../")
sys.path.append("../app")

from datetime import datetime, timedelta

from app            import create_app, db
from app.models     import ApiKey, Wallet, VirtualAccount
from app.config     import config

now = datetime.utcnow()

class TestConfig(config.Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

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


        key = ApiKey(label='SAMPLELABLE', name='SAMPLENAME')
        key.set_expiration(43800)
        key.revoke_access_key()

        self.assertEqual(key.expiration.hour,  (now + timedelta(seconds=1)).hour)
        self.assertEqual(key.expiration.minute,  (now + timedelta(seconds=1)).minute )

    def test_check_access_key(self):
        key = ApiKey(label='SAMPLELABLE', name='SAMPLENAME')
        key.generate_access_key(20)
        key.set_expiration(525600)
        db.session.add(key)
        db.session.commit()

        key_status = key.check_access_key("test")
        self.assertEqual(key_status, None)

        key_status = key.check_access_key("")
        self.assertEqual(key_status, None)


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
            name="lisa",
            msisdn="081212341234",
            email="lisa@bp.com",
        )
        db.session.add(wallet)
        db.session.commit()

        user = Wallet.query.get(1)
        balance = user.check_balance()
        self.assertEqual( balance, 0)

    def test_add_balance(self):
        wallet = Wallet(
            name="lisa",
            msisdn="081212341234",
            email="lisa@bp.com",
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
            name="lisa",
            msisdn="081212341234",
            email="lisa@bp.com",
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
            name="lisa",
            msisdn="081212341234",
            email="lisa@bp.com",
        )
        db.session.add(wallet)
        db.session.commit()

        user = Wallet.query.get(1)
        lock_status = user.is_unlocked()

        self.assertEqual( lock_status, True)

    def test_lock(self):
        wallet = Wallet(
            name="lisa",
            msisdn="081212341234",
            email="lisa@bp.com",
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
            name="lisa",
            msisdn="081212341234",
            email="lisa@bp.com",
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
            name="lisa",
            msisdn="081212341234",
            email="lisa@bp.com",
        )
        wallet.set_pin("123456")
        self.assertTrue( wallet.check_pin("123456") )
        self.assertFalse( wallet.check_pin("123654") )

    def test_generate_wallet_id(self):
        wallet_id = Wallet().generate_wallet_id()
        self.assertEqual( len(wallet_id), 12)


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
        va_number = VirtualAccount().generate_va_number()
        print(va_number)
        self.assertEqual(len(va_number), 16)

    def test_generate_trx_id(self):
        trx_id = VirtualAccount().generate_trx_id()
        print(trx_id)
        self.assertEqual(len(trx_id), 9)

if __name__ == "__main__":
    unittest.main(verbosity=2)
