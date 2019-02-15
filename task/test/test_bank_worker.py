from task.test.base import BaseTestCase

from app.api import db
from app.api.models import *

from task.bank.tasks import BankTask
from task.bank.tasks import TransactionTask

class TestBankWorker(BaseTestCase):
    """ Test Class for Bank Worker """

    def test_create_va(self):
        """ test function that create va in the background """
        # first create a dummy va first
        # create dummy wallet here
        wallet = Wallet(
        )
        db.session.add(wallet)
        db.session.commit()

        # create bank here
        bni = Bank(
            key="BNI"
        )
        db.session.add(bni)
        db.session.commit()

        va_credit = VaType(
            key="CREDIT"
        )
        db.session.add(va_credit)
        db.session.commit()

        # create virtual account credit
        va = VirtualAccount(
            amount="0",
            name="Lisa",
            wallet_id=wallet.id,
            bank_id=bni.id,
            va_type_id=va_credit.id
        )
        va_id = va.generate_va_number()
        trx_id = va.generate_trx_id()
        datetime_expired = va.get_datetime_expired("BNI", "CREDIT")
        db.session.add(va)
        db.session.commit()

        result = BankTask().create_va.delay(va_id)

    '''
    def test_bank_transfer(self):
        """ test function that transfer money using OPG in the background """
        bank = Bank.query.filter_by(code="009").first()

        bank_account = BankAccount(
            name="Lisa",
            bank_id=bank.id,
            account_no="11111111"
        )
        db.session.add(bank_account)
        db.session.commit()

        wallet = Wallet(
        )
        db.session.add(wallet)
        db.session.flush()

        # add some balance here for test case
        user = Wallet.query.get(1)
        user.add_balance(1000)
        db.session.flush()

        self.assertEqual(user.check_balance(), 1000)

        amount = -100

        payment_payload = {
            "payment_type"   : False,
            "source_account" : wallet.id,
            "to"             : bank_account.account_no,
            "amount"         : amount
        }

        payment = Payment(**payment_payload)
        db.session.add(payment)
        db.session.flush()

        debit_transaction = Transaction(
            payment_id=payment.id,
            wallet_id=wallet.id,
            amount=amount
        )
        debit_transaction.generate_trx_id()

        db.session.add(debit_transaction)

        wallet.add_balance(amount)

        result = BankTask().bank_transfer.delay(payment.id)
        print(result)
    '''

class TestTransactionTask(BaseTestCase):
    """ Test Class for Transaction Worker """
    def test_transfer(self):
        wallet = Wallet(
                 )
        db.session.add(wallet)
        db.session.flush()

        wallet2 = Wallet(
                 )
        db.session.add(wallet2)
        db.session.flush()

        # add some balance here for test case
        user = Wallet.query.get(1)
        user.add_balance(1000)
        db.session.flush()

        self.assertEqual(user.check_balance(), 1000)

        amount = -100

        payment_payload = {
            "payment_type"   : True,
            "source_account" : wallet.id,
            "to"             : wallet2.id,
            "amount"         : amount
        }

        payment = Payment(**payment_payload)
        db.session.add(payment)
        db.session.commit()

        result = TransactionTask().transfer.delay(payment.id)
