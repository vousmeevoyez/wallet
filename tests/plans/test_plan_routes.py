"""
    Test Payment Plan Routes
"""
import pytest
from datetime import datetime, timedelta

from tests.reusable.api_list import *

API_KEY = "8c574c41-3e01-4763-89af-fd370989da33"


def test_create_plan_auto(setup_additional_plan_for_auto):
    """ test routes function to create payment plan """
    # CREATE PAYMENT PLAN
    assert setup_additional_plan_for_auto["plan_id"]


def test_create_plan_auto_pay(setup_additional_plan_for_auto_pay):
    # create payment plan
    assert setup_additional_plan_for_auto_pay["plan_id"]


def test_create_plan_auto_debit(setup_additional_plan_for_auto_debit):
    assert setup_additional_plan_for_auto_debit["plan_id"]


def test_update_plan(client, setup_additional_plan_for_auto):
    """ test routes function to update plan """
    plan_id = setup_additional_plan_for_auto["plan_id"]

    params = {
        "payment_plan_id": "",  # we dont actualy need this! BAD
        "amount": "1000",
        "type": "ADDITIONAL",
        "due_date": "2020-12-12",
    }
    result = update_plan(client, plan_id, params, API_KEY)
    assert result.status_code == 204


# end def


def test_update_plan_status(client, setup_additional_plan_for_auto):
    """ test routes function to update plan """
    plan_id = setup_additional_plan_for_auto["plan_id"]

    params = {"status": "PAID"}
    result = update_plan_status(client, plan_id, params, API_KEY)
    assert result.status_code == 204

    params = {"status": "FAILED"}
    result = update_plan_status(client, plan_id, params, API_KEY)
    assert result.status_code == 204

    params = {"status": "STOPPED"}
    result = update_plan_status(client, plan_id, params, API_KEY)
    assert result.status_code == 204

    result = get_plan(client, plan_id, API_KEY)
    response = result.get_json()
    assert response["data"]["status"] == "STOPPED"
