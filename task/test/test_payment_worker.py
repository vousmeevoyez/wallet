from datetime import datetime
import time
from unittest.mock import patch

from celery.exceptions import Retry, MaxRetriesExceededError

from task.test.base import BaseTestCase

from app.api import db
from app.api.models import *
from app.api.http_response import *

from task.payment.tasks import PaymentTask

class TestBankWorker(BaseTestCase):
    """ Test Class for Bank Worker """
    
    def test_background_transfer(self):
        """ test function that transfer money using OPG in the background but
        failed and reach max retries """
        # create payment plan
        payment_plan = PaymentPlan(
            destination="12345678910",
            wallet_id=self.source.id
        )
        db.session.add(payment_plan)
        db.session.commit()

        # create plan
        monthly_plan = Plan(
            payment_plan_id=payment_plan.id,
            amount=10000,
            due_date=datetime.utcnow()
        )
        db.session.add(monthly_plan)
        db.session.commit()

        # register bank account
        bank = Bank.query.filter_by(code="009").first()

        bank_account = BankAccount(
            name="Lisa",
            bank_id=bank.id,
            account_no="12345678910"
        )
        db.session.add(bank_account)
        db.session.commit()

        result = PaymentTask().background_transfer.delay(monthly_plan.id)
        print(result.get())
