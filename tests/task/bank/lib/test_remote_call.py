"""
    Test Client Fetch
"""
from unittest import mock

from task.bank.lib.remote_call import fetch
from task.bank.lib.request import HTTPRequest
from task.bank.lib.response import HTTPResponse


def test_fetch():
    # prepare request
    request = HTTPRequest()
    request.url = "https://apibeta.bni-ecollection.com/"
    request.method = "POST"
    payload = {
        "type": "createbilling",
        "client_id": "99099",
        "trx_id": "12345",
        "trx_amount": "100",
        "billing_type": "j",
        "customer_name": "Kelvin",
        "customer_email": "",
        "customer_phone": "",
        "virtual_account": "",
        "datetime_expired": "",
        "description": "",
    }
    request.payload = payload

    response = HTTPResponse()

    response = fetch(request, response)
    assert response == {'status': '009', 'message': 'Unexpected Error.'}
