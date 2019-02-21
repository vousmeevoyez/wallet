from task.test.base import BaseTestCase

from app.api import db
from app.api.models import *

from task.bank.tasks import BankTask

class TestBankWorker(BaseTestCase):
    """ Test Class for Bank Worker """
    '''
    def test_create_va(self):
        """ test function that create va in the background """
        # first create a dummy va first
        # create dummy wallet here
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
            wallet_id=self.source.id,
            bank_id=bni.id,
            va_type_id=va_credit.id
        )
        va_id = va.generate_va_number()
        trx_id = va.generate_trx_id()
        datetime_expired = va.get_datetime_expired("BNI", "CREDIT")
        db.session.add(va)
        db.session.commit()

        result = BankTask().create_va.delay(va.id)
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

        amount = -100

        payment_payload = {
            "payment_type"   : False,
            "source_account" : self.source.id,
            "to"             : bank_account.account_no,
            "amount"         : amount
        }

        payment = Payment(**payment_payload)
        db.session.add(payment)

        debit_transaction = Transaction(
            payment_id=payment.id,
            wallet_id=self.source.id,
            amount=amount
        )
        debit_transaction.generate_trx_id()

        db.session.add(debit_transaction)
        db.session.commit()

        result = BankTask().bank_transfer.delay(payment.id)
        print(result)
