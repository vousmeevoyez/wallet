"""
    Test Base Http Request
    ______________
"""
from task.bank.lib.request import HTTPRequest


class TestHTTPRequest:
    """ Test HTTP Base Request """

    def test_setup_header(self):
        """ test method for setup a http request header """
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

        http_request = HTTPRequest()
        http_request.url = "https://apibeta.bni-ecollection.com/"
        http_request.method = "POST"
        http_request.payload = payload
        expected_result = {
            "url": "https://apibeta.bni-ecollection.com/",
            "method": "POST",
            "data": {
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
            },
            "headers": {"Content-Type": "application/json"},
        }

        request = http_request.to_representation()
        assert request["url"]
        assert request["method"]
        assert request["data"]
        assert request["headers"]
