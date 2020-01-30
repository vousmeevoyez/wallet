"""
    Test Plan Services
"""
from datetime import datetime

from app.api.models import *
from app.api import db

from app.api.plans.modules.plan_services import PlanServices


def test_add(setup_wallet_without_balance):
    """ test method for plan """
    payment_plan = PaymentPlan(
        wallet_id=setup_wallet_without_balance.id,
        destination="some-bank-account-number",
    )
    db.session.add(payment_plan)
    db.session.commit()

    plan = Plan(amount=1000, due_date=datetime(2019, 4, 25))

    result = PlanServices(payment_plan_id=payment_plan.id).add(plan)
    assert result[1] == 201
    assert result[0]["data"]["plan_id"]

    plan = Plan(amount=1000, due_date=datetime(2019, 5, 25))

    result = PlanServices(payment_plan_id=payment_plan.id).add(plan)
    assert result[1] == 201
    assert result[0]["data"]["plan_id"], "some-plan-id"


def test_add_auto_pay(setup_wallet_without_balance):
    """ test method for adding plan but setting auto pay"""
    payment_plan = PaymentPlan(
        wallet_id=setup_wallet_without_balance.id,
        method=2,  # set to auto pay
        destination="some-bank-account-number",
    )
    db.session.add(payment_plan)
    db.session.commit()

    plan = Plan(amount=1000, type=1, due_date=datetime(2019, 4, 25))  # additional

    result = PlanServices(payment_plan_id=payment_plan.id).add(plan)
    assert result[1] == 201
    assert result[0]["data"]["plan_id"]


def test_show(setup_wallet_without_balance):
    """ test method for showing plan """
    payment_plan = PaymentPlan(
        wallet_id=setup_wallet_without_balance.id,
        destination="some-bank-account-number",
    )
    db.session.add(payment_plan)
    db.session.commit()

    plan = Plan(amount=1000, due_date=datetime(2019, 4, 25))

    result = PlanServices(payment_plan_id=payment_plan.id).add(plan)
    assert result[1] == 201
    assert result[0]["data"]["plan_id"]

    result = PlanServices.show()
    assert result[0]["data"]


def test_info(setup_wallet_with_balance):
    """ test method for info plan """
    payment_plan = PaymentPlan(
        wallet_id=setup_wallet_with_balance.id, destination="some-bank-account-number"
    )
    db.session.add(payment_plan)
    db.session.commit()

    plan = Plan(amount=1000, due_date=datetime(2019, 4, 25))

    result = PlanServices(payment_plan_id=payment_plan.id).add(plan)
    assert result[1] == 201
    assert result[0]["data"]["plan_id"]

    plan_id = result[0]["data"]["plan_id"]

    result = PlanServices(plan_id=plan_id).info()
    assert result[0]["data"]


def test_update(setup_wallet_with_balance):
    """ test method for info plan """
    payment_plan = PaymentPlan(
        wallet_id=setup_wallet_with_balance.id, destination="some-bank-account-number"
    )
    db.session.add(payment_plan)
    db.session.commit()

    plan = Plan(amount=1000, due_date=datetime(2019, 4, 25))

    result = PlanServices(payment_plan_id=payment_plan.id).add(plan)
    assert result[1] == 201
    assert result[0]["data"]["plan_id"]

    plan = Plan(amount=1111, due_date=datetime(2019, 3, 25))
    plan_id = result[0]["data"]["plan_id"]

    result = PlanServices(plan_id=plan_id).update(plan)
    assert result[1] == 204


def test_update_status(setup_wallet_with_balance):
    """ test method for info plan """
    payment_plan = PaymentPlan(
        wallet_id=setup_wallet_with_balance.id, destination="some-bank-account-number"
    )
    db.session.add(payment_plan)
    db.session.commit()

    plan = Plan(amount=1000, due_date=datetime(2019, 4, 25))

    result = PlanServices(payment_plan_id=payment_plan.id).add(plan)
    assert result[1] == 201
    assert result[0]["data"]["plan_id"]

    plan_id = result[0]["data"]["plan_id"]

    result = PlanServices(plan_id=plan_id).update_status({"status": "PENDING"})
    assert result[1] == 204

    result = PlanServices(plan_id=plan_id).update_status({"status": "RETRYING"})
    assert result[1] == 204

    result = PlanServices(plan_id=plan_id).update_status({"status": "PAID"})
    assert result[1] == 204

    result = PlanServices(plan_id=plan_id).update_status({"status": "SENDING"})
    assert result[1] == 204

    result = PlanServices(plan_id=plan_id).update_status({"status": "FAIL"})
    assert result[1] == 204


def test_remove(setup_wallet_with_balance):
    """ test method for remove plan """
    payment_plan = PaymentPlan(
        wallet_id=setup_wallet_with_balance.id, destination="some-bank-account-number"
    )
    db.session.add(payment_plan)
    db.session.commit()

    plan = Plan(amount=1000, due_date=datetime(2019, 4, 25))

    result = PlanServices(payment_plan_id=payment_plan.id).add(plan)
    assert result[1] == 201
    assert result[0]["data"]["plan_id"]

    plan_id = result[0]["data"]["plan_id"]

    result = PlanServices(plan_id=plan_id).remove()
    assert result[1] == 204
