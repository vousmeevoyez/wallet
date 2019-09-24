import time
import random

from unittest.mock import patch
from faker import Faker

from celery.exceptions import Retry, MaxRetriesExceededError

from task.test.base import BaseTestCase

from app.api import db
from app.api.models import (
    VirtualAccount,
    VaType,
    VaLog,
    Bank,
    Transaction,
    BalanceLog,
    Wallet
)
from app.api.serializer import VirtualAccountSchema

from task.logger.tasks import LoggingTask


class TestLoggingWorker(BaseTestCase):
    """ Test Class for logging Worker """

    def _create_dummy_wallet_balance(self, count=100):
        balance = random.randint(1, 10000000)
        for x in range(count):
            wallet = Wallet(balance=balance)
            db.session.add(wallet)
            db.session.commit()
        # end for

    def _create_va(self, count=100):
        # credit
        va_credit = VaType(key="CREDIT")
        db.session.add(va_credit)
        db.session.commit()

        # create bank here
        bank = Bank(key="BNI", name="Bank BNI", code="009")
        db.session.add(bank)
        db.session.commit()

        for x in range(count):
            # create virtual account credit
            faker = Faker("en_US")
            fake_name = faker.name()
            va = VirtualAccount(
                amount="100",
                name=fake_name,
                va_type_id=va_credit.id,
                bank_id=bank.id,
            )
            va.generate_va_number()
            va.generate_trx_id()
            va.get_datetime_expired("BNI", "CREDIT")
            db.session.add(va)
            db.session.commit()

    def test_fetch_va(self):
        """ test function that transfer money using OPG in the background but
        failed and reach max retries """
        self._create_va()

        # create payment plan
        result = LoggingTask().fetch_va.apply_async(args=[], queue="logging")
        #print(result.get())
        logs = VaLog.query.all()
        self.assertEqual(len(logs), 100)

    def test_record_external_balance(self):
        """ test background task that periodically check external balance and
        compare it with our internal balance """
        # create a set of dummy transaction
        self._create_dummy_wallet_balance(1000)

        result = LoggingTask().record_external_balance.apply_async(
            args=[], queue="logging"
        )
        # must added to make sure the task finished before we end the unittest
        #print(result.get())
