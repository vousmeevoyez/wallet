import json
import random

from app.api.models import *

from app.api.callback.modules.callback_services import *


def test_process(setup_credit_va):
    """ testing base process class """
    va = setup_credit_va[2]

    ref_number = random.randint(11111111, 9999999999)

    payment_amount = 10000
    transfer_types = "TOP_UP"
    channel = "BNI_VA"
    result = Callback(va.account_no, va.trx_id, "IN").process(
        payment_amount, transfer_types, ref_number, channel
    )
    assert result["status"] == "000"


def test_deposit(setup_credit_va):
    """ test deposit """
    va = setup_credit_va[2]

    ref_number = random.randint(11111111, 9999999999)

    params = {
        "payment_amount": 10000,
        "payment_ntb": str(ref_number),
        "payment_channel_key": "BNI_VA",
    }
    result = CallbackServices(va.account_no, va.trx_id, "IN").process_callback(params)
    assert result["status"] == "000"


def test_withdraw(setup_debit_va):
    """ test deposit """
    account_no = setup_debit_va[0]
    trx_id = setup_debit_va[1]

    ref_number = random.randint(11111111, 9999999999)

    params = {
        "payment_amount": -10000,
        "payment_ntb": str(ref_number),
        "payment_channel_key": "BNI_VA",
    }
    result = CallbackServices(account_no, trx_id, "OUT").process_callback(params)

    assert result["status"] == "000"
