"""
    Test Payment Plan Services
"""
import uuid
from datetime import datetime
from unittest.mock import patch, Mock

from app.api.models import *

from app.api.payment_plans.modules.payment_plan_services import PaymentPlanServices

# exceptions
from app.lib.http_error import *


def test_add_without_id(setup_wallet_info):
    """ test method for adding payment plan and plan """
    plans = []
    plan = Plan(amount=100, due_date=datetime(2019, 1, 5))

    plan2 = Plan(amount=100, due_date=datetime(2019, 2, 1))
    plans.append(plan)
    plans.append(plan2)

    payment_plan = PaymentPlan(destination="some-bank-account-number", plans=plans)

    result = PaymentPlanServices(setup_wallet_info["id"]).add(payment_plan)
    assert result[1] == 201
    assert result[0]["data"]["payment_plan_id"]


def test_add_with_id(setup_wallet_info):
    """ test method for adding payment plan and plan """
    plans = []
    plan = Plan(amount=100, due_date=datetime(2019, 1, 3))

    plan2 = Plan(amount=100, due_date=datetime(2019, 2, 4))
    plans.append(plan)
    plans.append(plan2)

    payment_plan_id = "test-add-some-payment-plan-id"
    payment_plan = PaymentPlan(
        id=payment_plan_id, destination="some-bank-account-number", plans=plans
    )

    result = PaymentPlanServices(setup_wallet_info["id"]).add(payment_plan)
    assert result[1] == 201
    assert result[0]["data"]["payment_plan_id"] == payment_plan_id


def test_add_but_auto_pay(setup_wallet_info):
    """ test method for adding payment plan and plan but repayment using
    auto pay """
    plans = []
    plan = Plan(amount=100, due_date=datetime(2019, 1, 5))

    plan2 = Plan(amount=100, due_date=datetime(2019, 2, 1))
    plans.append(plan)
    plans.append(plan2)

    payment_plan = PaymentPlan(
        destination="some-bank-account-number",
        plans=plans,
        method=2,  # mark payment as auto pay
    )

    result = PaymentPlanServices(setup_wallet_info["id"]).add(payment_plan)
    assert result[1] == 201
    assert result[0]["data"]["payment_plan_id"]


def test_add_bank_account_already_exist(setup_wallet_info):
    """ test method for adding payment plan and plan """
    plans = []
    plan = Plan(amount=100, due_date=datetime(2019, 1, 1))

    plan2 = Plan(amount=100, due_date=datetime(2019, 2, 1))
    plans.append(plan)
    plans.append(plan2)

    payment_plan = PaymentPlan(destination="some-bank-account-number", plans=plans)

    result = PaymentPlanServices(setup_wallet_info["id"]).add(payment_plan)
    assert result[1] == 201
    assert result[0]["data"]["payment_plan_id"]


def test_show(setup_wallet_info):
    """ test method for showing all payment plan """
    result = PaymentPlanServices.show()
    assert len(result[0]["data"]) > 0


def test_info(setup_wallet_info):
    """ test method for single payment plan """
    payment_plan_id = "test-add-some-payment-plan-id"
    result = PaymentPlanServices(payment_plan_id=payment_plan_id).info()
    assert result[0]["data"]


def test_update(setup_wallet_info):
    """ test method for updating payment plan """
    payment_plan_id = "test-add-some-payment-plan-id"
    params = {"destination": "123123123123", "status": False}

    result = PaymentPlanServices(
        payment_plan_id=payment_plan_id, wallet_id=setup_wallet_info["id"]
    ).update(params)
    assert result[1] == 204


def test_remove(setup_wallet_info):
    """ test method for removing payment plan """
    payment_plan_id = "test-add-some-payment-plan-id"

    result = PaymentPlanServices(payment_plan_id=payment_plan_id).remove()
    assert result[1] == 204
