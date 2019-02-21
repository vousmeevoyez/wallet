import time
from task.test.base import BaseTestCase

from app.api import db
from app.api.models import *

from task.transaction.tasks import TransactionTask

class TestTransactionTask(BaseTestCase):
    """ Test Class for Transaction Worker """
    def test_bulk_transfer(self):
        # add some balance here for test case
        for i in range(0, 100):
            self._transfer(self.source, self.destination, 1)
            self._transfer(self.destination, self.source, 1)
        #end for
        time.sleep(3)
        source = Wallet.query.get(1)
        destination = Wallet.query.get(2)
        self.assertEqual(source.balance, 100)
        self.assertEqual(destination.balance, 100)
    #end for

    def _transfer(self, source, destination, amount):
        # DEBIT
        payment_payload = {
            "payment_type"   : False,
            "source_account" : source.id,
            "to"             : destination.id,
            "amount"         : -amount
        }

        debit = Payment(**payment_payload)
        db.session.add(debit)
        db.session.commit()

        result = TransactionTask().transfer.delay(debit.id)

        # CREDIT
        payment_payload = {
            "payment_type"   : True,
            "source_account" : source.id,
            "to"             : destination.id,
            "amount"         : amount
        }

        credit = Payment(**payment_payload)
        db.session.add(credit)
        db.session.commit()

        result = TransactionTask().transfer.delay(credit.id)
