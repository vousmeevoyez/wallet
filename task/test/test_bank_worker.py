from task.test.base import BaseTestCase

from app.api import db
from app.api.models import *

from task.bank.tasks import create_va

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
            trx_amount="0",
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

        result = create_va.delay(va_id)
        result.wait()
