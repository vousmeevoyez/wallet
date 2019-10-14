"""
    Test Payment Plan Routes
"""
from datetime import datetime, timedelta

from tests.reusable.api_list import *


API_KEY = "8c574c41-3e01-4763-89af-fd370989da33"


def test_create_payment_plan_auto(setup_payment_plan_auto):
    """ test routes function to create payment plan """
    assert setup_payment_plan_auto["payment_plan_id"]


def test_create_payment_plan_auto_pay(setup_payment_plan_auto_pay):
    assert setup_payment_plan_auto_pay["payment_plan_id"]


def test_create_payment_plan_auto_debit(setup_payment_plan_auto_debit):
    assert setup_payment_plan_auto_debit["payment_plan_id"]


def test_get_payment_plans(client, setup_payment_plan_auto):
    """ test routes function to get payment plans"""
    result = get_payment_plans(client, API_KEY)
    response = result.get_json()
    assert len(response["data"]) > 0


def test_get_payment_plan(client, setup_payment_plan_auto):
    """ test routes function to get payment plan"""
    payment_plan_id = setup_payment_plan_auto["payment_plan_id"]
    result = get_payment_plan(client, payment_plan_id, API_KEY)

    response = result.get_json()
    assert response["data"]


def test_update_payment_plan(client, setup_payment_plan_auto, setup_wallet_info):
    """ test routes function to update payment plan"""
    payment_plan_id = setup_payment_plan_auto["payment_plan_id"]

    params = {
        "destination": "654321",
        "wallet_id": setup_wallet_info["id"],
        "method": "AUTO_PAY",
        "status": "DEACTIVE",
    }
    result = update_payment_plan(client, payment_plan_id, params, API_KEY)
    assert result.status_code == 204


def test_remove_payment_plan(client, setup_payment_plan_auto):
    """ test routes function to get payment plan"""
    payment_plan_id = setup_payment_plan_auto["payment_plan_id"]
    result = remove_payment_plan(client, payment_plan_id, API_KEY)
    assert result.status_code == 204
