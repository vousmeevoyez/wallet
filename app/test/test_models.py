""" 
    Test Models
    ___________
    test all module here
"""
from datetime import datetime, timedelta

from app.test.base  import BaseTestCase
from app.api        import db
from app.api.models import *
from app.config import config

from app.api.exception.authentication import *

from sqlalchemy.exc import IntegrityError, InvalidRequestError

class UserTestCaseModel(BaseTestCase):
    """ Test User Model"""
    def test_user_role_relation(self):
        """ test relationship between User & Role"""
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
            username='janejane',
            name='jane',
            email='jane@bp.com',
            phone_ext='62',
            phone_number='82229644314',
            role_id=role.id,
        )
        user2.set_password("password")
        db.session.add(user2)
        db.session.commit()

        # get user by their role
        self.assertEqual( len(role.user), 2)

    def test_wallet_relation(self):
        """ test relationship between User & Wallet """
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

        user = User.query.get(3)
        # check how many wallet user have
        self.assertEqual( len(user.wallets), 1)

    def test_password(self):
        """ test generate password"""
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

    def test_encode_token(self):
        """ test encode a token"""
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

        token = user.encode_token("ACCESS", user.id, user.role.description)
        self.assertTrue(isinstance(token, bytes))

    def test_decode_token(self):
        """ test decode token"""
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

        token = user.encode_token("ACCESS", user.id, user.role.description)
        self.assertTrue(isinstance(token, bytes))

        token = token.decode("utf-8")

        # make sure the decoded token contain following information
        self.assertEqual(user.decode_token(token)["type"], "ACCESS")
        self.assertEqual(user.decode_token(token)["role"], "USER")

        with self.assertRaises(EmptyPayloadError):
            user.decode_token("eyJhbGciOiJIUzI1NiIsInR5cCI6Im5vbmUifQ.e30.kligm-MjaliTD584hBs6v52XSZcixYU9BlmAAwmjOB0")

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
        self.assertEqual( lock_status, 3)

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

        result = Wallet.is_owned(3, wallet_id)
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
        datetime_expired = va.get_datetime_expired("BNI", "CREDIT")
        db.session.add(va)
        db.session.commit()

        va_number = va.generate_va_number()
        self.assertEqual(len(va_number), 16)

class MasterTransactionModelCase(BaseTestCase):

    @staticmethod
    def _create_payment(source, destination, amount, payment_type):
        db.session.begin()
        try:
            payment = Payment(
                source_account=source,
                to=destination,
                amount=amount,
                payment_type=payment_type,
            )
            db.session.add(payment)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        #end try
    #end def

    @staticmethod
    def _create_transaction(wallet_id, amount):
        db.session.begin()
        try:
            transaction = Transaction(
                wallet_id=wallet_id,
                amount=amount,
            )
            transaction.generate_trx_id()
        except IntegrityError:
            db.session.rollback()
        #end try
    #end def
    def test_master_transaction(self):
        # create 2 dummy wallet here
        wallet = Wallet(
        )
        wallet2 = Wallet(
        )

        db.session.add(wallet)
        db.session.add(wallet2)
        db.session.flush()

        # add some balance here for test case
        user = Wallet.query.get(1)
        user.add_balance(1000)
        db.session.flush()

        self.assertEqual(user.check_balance(), 1000)

        user2 = Wallet.query.get(2)
        user2.add_balance(1000)
        db.session.flush()

        self.assertEqual(user2.check_balance(), 1000)

        # INITIALIZE TRANSACTION
        trx_amount = -10
        # master transaction
        master_debit_trx = MasterTransaction(
            source=wallet.id,
            destination=wallet2.id,
            amount=trx_amount,
        )
        db.session.add(master_debit_trx)

        user.add_balance(trx_amount)

        # SET TO PENDING AFTER DEDUCT BALANCE
        master_debit_trx.state = 1 # pending
        db.session.flush()

        # log debit transaction journal here

        #create debit transaction
        debit_trx = Transaction(
            wallet_id=wallet.id,
            amount=trx_amount,
        )
        debit_trx.generate_trx_id()
        db.session.add(debit_trx)
        # deduct balance
        db.session.flush()

        master_debit_trx.state = 2 # pending
        master_debit_trx.transaction_id = debit_trx.id
        db.session.commit()

        trx_amount = 10
        master_credit_trx = MasterTransaction(
            source=wallet2.id,
            destination=wallet.id,
            amount=trx_amount,
        )

        # CREDIT BALANCE HERE
        user2.add_balance(trx_amount)
        # SET TRANSACTION TO COMPLETE
        master_credit_trx.state = 1
        db.session.flush()

        #start another transaction here
        # second create credit payment
        credit_payment = Payment(
            source_account=wallet.id,
            to=wallet2.id,
            amount=trx_amount,
        )
        db.session.add(credit_payment)

        #create debit transaction
        credit_trx = Transaction(
            wallet_id=wallet2.id,
            amount=trx_amount,
        )
        credit_trx.generate_trx_id()
        db.session.add(credit_trx)
        # deduct user balance here
        master_credit_trx.state = 2 # pending
        master_credit_trx.transaction_id = credit_trx.id

        db.session.commit()
        # make sure each account have correct balance after each transaction
        user = Wallet.query.get(1)
        self.assertEqual(user.check_balance(), 990)
        self.assertEqual(len(user.transactions), 1)

        user2 = Wallet.query.get(2)
        self.assertEqual(user2.check_balance(), 1010)
        self.assertEqual(len(user2.transactions), 1)

        master_trx = MasterTransaction.query.all()
        self.assertTrue(len(master_trx) > 0)

class TransactionModelCase(BaseTestCase):

    def test_debit_transaction(self):
        # create 2 dummy wallet here
        wallet = Wallet(
        )
        wallet2 = Wallet(
        )

        db.session.add(wallet)
        db.session.add(wallet2)
        db.session.flush()

        # add some balance here for test case
        user = Wallet.query.get(1)
        user.add_balance(1000)
        db.session.flush()

        self.assertEqual(user.check_balance(), 1000)

        user2 = Wallet.query.get(2)
        user2.add_balance(1000)
        db.session.flush()

        self.assertEqual(user2.check_balance(), 1000)

        #start transaction here
        trx_amount = -10
        # first create debit payment
        debit_payment = Payment(
            source_account=wallet.id,
            to=wallet2.id,
            amount=trx_amount,
            payment_type=False,
        )
        db.session.add(debit_payment)

        #create debit transaction
        debit_trx = Transaction(
            wallet_id=wallet.id,
            amount=trx_amount,
        )
        debit_trx.generate_trx_id()
        db.session.add(debit_trx)
        # deduct balance
        user.add_balance(trx_amount)

        db.session.flush()

        #start another transaction here
        trx_amount = 10
        # second create credit payment
        credit_payment = Payment(
            source_account=wallet.id,
            to=wallet2.id,
            amount=trx_amount,
        )
        db.session.add(credit_payment)

        #create debit transaction
        credit_trx = Transaction(
            wallet_id=wallet2.id,
            amount=trx_amount,
        )
        credit_trx.generate_trx_id()
        db.session.add(credit_trx)
        # deduct user balance here
        user2.add_balance(trx_amount)

        db.session.flush()

        # make sure each account have correct balance after each transaction
        user = Wallet.query.get(1)
        self.assertEqual(user.check_balance(), 990)
        self.assertEqual(len(user.transactions), 1)

        user2 = Wallet.query.get(2)
        self.assertEqual(user2.check_balance(), 1010)
        self.assertEqual(len(user2.transactions), 1)

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

    def test_check_valid_otp_log(self):
        # create wallet
        wallet = Wallet(
        )
        db.session.add(wallet)
        db.session.commit()

        wallet = Wallet.query.get(1)

        # create forgot pin record
        valid_until = datetime.now() + timedelta(minutes=5)

        forgot_pin = ForgotPin(
            wallet_id=wallet.id,
            valid_until=valid_until
        )
        forgot_pin.set_otp_code("123456")
        db.session.add(forgot_pin)
        db.session.commit()

        # check record and make sure there's a pending otp record
        result = ForgotPin.query.filter(ForgotPin.wallet_id==wallet.id, ForgotPin.status==False, ForgotPin.valid_until > datetime.now()).count()
        self.assertEqual(result, 1)

    def test_check_invalid_otp_log(self):
        # create wallet
        wallet = Wallet(
        )
        db.session.add(wallet)
        db.session.commit()

        wallet = Wallet.query.get(1)

        # create forgot pin record
        valid_until = datetime.now() - timedelta(minutes=5)

        forgot_pin = ForgotPin(
            wallet_id=wallet.id,
            valid_until=valid_until
        )
        forgot_pin.set_otp_code("123456")
        db.session.add(forgot_pin)
        db.session.commit()

        # check record and make sure there's a pending otp record
        result = ForgotPin.query.filter(ForgotPin.wallet_id==wallet.id, ForgotPin.status==False, ForgotPin.valid_until > datetime.now()).count()
        self.assertEqual(result, 0)

class WithdrawModelCase(BaseTestCase):

    def test_withdraw_wallet(self):
        # create wallet
        wallet = Wallet(
        )
        db.session.add(wallet)
        db.session.commit()

        wallet = Wallet.query.get(1)

        # create forgot pin record
        valid_until = datetime.now() - timedelta(minutes=5)

        withdraw= Withdraw(
            wallet_id=wallet.id,
            valid_until=valid_until
        )
        db.session.add(withdraw)
        db.session.commit()

        # check record and make sure there's a pending otp record
        result = Withdraw.query.filter(Withdraw.wallet_id==wallet.id, Withdraw.valid_until > datetime.now()).count()
        self.assertEqual(result, 0)

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
            name="Ririn",
            bank_id=bca.id,
            user_id=user.id
        )
        db.session.add(bank_account)
        db.session.commit()

        # make sure user is associated to bank account
        print(user.bank_accounts)
        self.assertEqual( len(user.bank_accounts), 2)

class PaymentChannelModelCase(BaseTestCase):
    def test_payment_channel(self):
        # create bank here
        bni=Bank(
            key="BNI",
            name="Bank BNI",
            code="99",
        )
        db.session.add(bni)
        db.session.commit()

        # create payment channel
        payment_channel1 = PaymentChannel(
            name="BNI Virtual Account",
            key="BNI_VA",
            channel_type="VIRTUAL_ACCOUNT",
            bank_id=bni.id
        )
        db.session.add(payment_channel1)

        # create payment channel
        payment_channel2 = PaymentChannel(
            name="BNI Transfer",
            key="BNI_TRANSFER",
            channel_type="TRANSFER",
            bank_id=bni.id
        )
        db.session.add(payment_channel2)
        db.session.commit()

        self.assertEqual(len(bni.payment_channels), 2)
    #end def
#end class

class PaymentModelCase(BaseTestCase):

    def test_payment_model(self):
        # create bank here
        bni=Bank(
            key="BNI",
            name="Bank BNI",
            code="99",
        )
        db.session.add(bni)
        db.session.commit()

        # create payment channel
        payment_channel1 = PaymentChannel(
            name="BNI Virtual Account",
            key="BNI_VA",
            channel_type="VIRTUAL_ACCOUNT",
            bank_id=bni.id
        )
        db.session.add(payment_channel1)

        # create payment channel
        payment_channel2 = PaymentChannel(
            name="BNI Transfer",
            key="BNI_TRANSFER",
            channel_type="TRANSFER",
            bank_id=bni.id
        )
        db.session.add(payment_channel2)
        db.session.flush()

        # payment
        payment = Payment(
            source_account="123456",
            ref_number="111111",
            amount=1,
            to="123",
            channel_id=payment_channel1.id,
        )
        db.session.add(payment)

        # payment 2
        payment2 = Payment(
            source_account="133456",
            ref_number="111112",
            amount=2,
            channel_id=payment_channel2.id,
            to="123"
        )
        db.session.add(payment2)
        db.session.commit()

        payments = Payment.query.join(PaymentChannel).join(Bank).filter(PaymentChannel.bank_id==bni.id).all()
        self.assertEqual(len(payments), 2)
    #end def
#end class

if __name__ == "__main__":
    unittest.main(verbosity=2)
