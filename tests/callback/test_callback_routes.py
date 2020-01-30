"""
    Integration Testing between wallet & routes
"""
from task.bank.lib.helper import encrypt

from app.config.external.bank import BNI_ECOLLECTION

from tests.reusable.api_list import deposit_callback, withdraw_callback


def test_deposit_callback(client, setup_wallet_info):
    """ DEPOSIT CALLBACK CASE 1 : Successfully deposit callback """
    wallet_info = setup_wallet_info

    data = {
        "virtual_account": wallet_info["virtual_accounts"][0]["account_no"],
        "customer_name": "jennie",
        "trx_id": wallet_info["virtual_accounts"][0]["trx_id"],
        "trx_amount": "0",
        "payment_amount": "50000",
        "cumulative_payment_amount": "50000",
        "payment_ntb": "12345",
        "datetime_payment": "2018-12-20 11:16:00",
    }
    # generate encrypted data using BNI encryption
    encrypted_data = encrypt(
        BNI_ECOLLECTION["CREDIT_CLIENT_ID"], BNI_ECOLLECTION["CREDIT_SECRET_KEY"], data
    )

    fake_callback_request = {
        "client_id": BNI_ECOLLECTION["CREDIT_CLIENT_ID"],
        "data": encrypted_data,
    }
    result = deposit_callback(client, fake_callback_request)
    response = result.get_json()
    assert response["status"] == "000"


def test_withdraw_callback(client, setup_wallet_info):
    """ WITHDRAW CALLBACK CASE 1 : Successfully withdraw callback """

    wallet_info = setup_wallet_info

    data = {
        "virtual_account": wallet_info["virtual_accounts"][0]["account_no"],
        "customer_name": "jennie",
        "trx_id": wallet_info["virtual_accounts"][0]["trx_id"],
        "trx_amount": "0",
        "payment_amount": "-50000",
        "cumulative_payment_amount": "-50000",
        "payment_ntb": "12348",
        "datetime_payment": "2018-12-20 11:16:00",
    }

    encrypted_data = encrypt(
        BNI_ECOLLECTION["DEBIT_CLIENT_ID"], BNI_ECOLLECTION["DEBIT_SECRET_KEY"], data
    )

    fake_callback_request = {
        "client_id": BNI_ECOLLECTION["DEBIT_CLIENT_ID"],
        "data": encrypted_data,
    }

    result = withdraw_callback(client, fake_callback_request)
    response = result.get_json()

    assert response["status"] == "000"
