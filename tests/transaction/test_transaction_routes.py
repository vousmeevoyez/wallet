"""
    Integration Testing between wallet & routes
"""
import uuid
from unittest.mock import Mock, patch

from app.api.models import User
from app.api.models import Wallet
from app.api import db

from tests.reusable.api_list import transfer, refund_transaction

'''
"""
    GET TRANSACTIONS
"""
def test_get_transactions(self):
    """ GET TRANSACTIONS CASE 1 : Get wallet transaction for specific date"""
    # TEST GETTING IN TRANSACTION
    params = {
        "start_date" : "2019/01/01",
        "end_date"   : "2019/01/03",
        "flag" : "IN"
    }
    result = self.get_transaction(self._wallet1, params, self._token)
    response = result.get_json()
    self.assertTrue(result.status_code, 200)
    # TEST GETTING OUT TRANSACTION
    params = {
        "start_date" : "2019/01/01",
        "end_date"   : "2019/01/03",
        "flag" : "OUT"
    }
    result = self.get_transaction(self._wallet1, params, self._token)
    response = result.get_json()
    self.assertTrue(result.status_code, 200)
    #TEST GETTING ALL TRANSACTIONS
    params = {
        "start_date" : "2019/01/01",
        "end_date"   : "2019/01/03",
        "flag" : "ALL"
    }
    result = self.get_transaction(self._wallet1, params, self._token)
    response = result.get_json()
    self.assertTrue(result.status_code, 200)

def test_get_transactions_serialize_failed(self):
    """ GET TRANSACTIONS CASE 2 : Get wallet transaction with invalid
    payload """
    # TEST GETTING IN TRANSACTION
    params = {
        "start_date" : "2019-01-01",
        "end_date"   : "2019-01-03",
        "flag" : "KLK"
    }
    result = self.get_transaction(self._wallet1, params, self._token)
    response = result.get_json()
    self.assertTrue(result.status_code, 400)

"""
    TRANSACTION DETAILS
"""
def test_get_transactions_details(self):
    """ GET TRANSACTIONS DETAILS 1 : Get wallet transaction details but
    transaction not found"""
    params = {
        "transaction_id" : str(uuid.uuid4()),
    }
    result = self.get_transaction_details(self._wallet1, params, self._token)
    response = result.get_json()
    self.assertTrue(result.status_code, 404)
    self.assertEqual(response["error"], "TRANSACTION_NOT_FOUND")
    self.assertTrue(response["message"])
'''
"""
    REFUND
"""


def test_refund_transfer(client,
                         setup_user_wallet_va,
                         setup_user_wallet_va_without_balance,
                         setup_admin_token):
    """ CASE 1 Refund : successfully refund a transfer """

    source_access_token, source_user_id, source_wallet_id = \
    setup_user_wallet_va
    destination_access_token, destination_user_id, destination_wallet_id = \
    setup_user_wallet_va_without_balance

    params = {
        "amount": "1",
        "notes": "some notes",
        "pin": "123456",
        "types": "PAYROLL",
    }

    result = transfer(
        client,
        source_wallet_id,
        destination_wallet_id,
        params,
        source_access_token
    )
    response = result.get_json()

    assert result.status_code == 202
    assert response["data"]

    # get transaction id that going to be refunded
    transaction_id = response["data"]["id"]

    result = refund_transaction(client, transaction_id, setup_admin_token)
    response = result.get_json()

    assert result.status_code == 202
    assert response["data"]
