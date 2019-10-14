from datetime import datetime
import time
from unittest.mock import patch

from celery.exceptions import Retry, MaxRetriesExceededError

from app.api import db
from app.api.models import *
from app.api.http_response import *

from task.payment.tasks import PaymentTask


def test_background_transfer(setup_wallet_with_balance):
    """ test function that transfer money using OPG in the background but
    failed and reach max retries """
    # create payment plan
    payment_plan = PaymentPlan(destination="12345678910",
                               wallet_id=setup_wallet_with_balance.id)
    db.session.add(payment_plan)
    db.session.commit()

    # create plan
    monthly_plan = Plan(
        payment_plan_id=payment_plan.id, amount=100, due_date=datetime.utcnow()
    )
    db.session.add(monthly_plan)
    db.session.commit()

    # register bank account
    bank = Bank.query.filter_by(code="009").first()

    bank_account = BankAccount(
        name="Lisa", bank_id=bank.id, account_no="12345678910"
    )
    db.session.add(bank_account)
    db.session.commit()

    result = PaymentTask().background_transfer(monthly_plan.id, "AUTO_PAY")
    assert monthly_plan.status == 3


def test_background_transfer_but_already_paid(setup_wallet_with_balance):
    """ test background transfer for payment plan that already paid """
    # create payment plan
    payment_plan = PaymentPlan(destination="12345678910",
                               wallet_id=setup_wallet_with_balance.id)
    db.session.add(payment_plan)
    db.session.commit()

    # create plan
    monthly_plan = Plan(
        payment_plan_id=payment_plan.id,
        amount=100,
        status=3,
        due_date=datetime.utcnow(),
    )
    db.session.add(monthly_plan)
    db.session.commit()

    # register bank account
    bank = Bank.query.filter_by(code="009").first()

    bank_account = BankAccount(
        name="Lisa", bank_id=bank.id, account_no="12345678910"
    )
    db.session.add(bank_account)
    db.session.commit()

    result = PaymentTask().background_transfer(monthly_plan.id, "AUTO_PAY")
    assert result is False 
