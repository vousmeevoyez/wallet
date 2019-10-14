"""
    Test BNI Http Request
    ______________
"""
from task.bank.factories.request.va.request import (
    BNICreditEcollectionRequest,
    BNIDebitEcollectionRequest
)


class TestBNICreditEcollectionRequest:
    """ Test BNI E-Collection Credit Request """
    def test_set_payload(self):
        http_request = BNICreditEcollectionRequest()
        http_request.url = "https://apibeta.bni-ecollection.com/"
        http_request.method = "POST"

        payload = {
            "type": "createbilling",
            "trx_id": "41980682",
            "trx_amount": "100000",
            "billing_type": "d",
            "customer_name": "BL652M",
            "customer_email": "",
            "customer_phone": "628797655047",
            "virtual_account": "9889909667037879",
            "datetime_expired": "2019-09-12 11:45:07",
        }

        http_request.payload = payload

        request = http_request.to_representation()
        # make sure it all has this component
        assert request["url"]
        assert request["method"]
        assert request["headers"]
        assert request["data"]

    def test_get_payload(self):
        http_request = BNICreditEcollectionRequest()
        http_request.url = "https://apibeta.bni-ecollection.com/"
        http_request.method = "POST"

        payload = {
            "type": "createbilling",
            "trx_id": "41980682",
            "trx_amount": "100000",
            "billing_type": "d",
            "customer_name": "BL652M",
            "customer_email": "",
            "customer_phone": "628797655047",
            "virtual_account": "9889909667037879",
            "datetime_expired": "2019-09-12 11:45:07",
        }

        # set the request here
        http_request.payload = payload
        # get the request here
        request = http_request.payload
        # mandatory information!
        assert request["client_id"]
        assert request["data"]
        # data inside
        request_data = request["data"]
        assert request_data["type"]
        assert request_data["trx_id"]
        assert request_data["trx_amount"]
        assert request_data["billing_type"]
        assert request_data["customer_name"]
        assert request_data["customer_email"] == ""
        assert request_data["description"] == ""
        assert request_data["customer_phone"]
        assert request_data["virtual_account"]
        assert request_data["datetime_expired"]
        assert request_data["client_id"]
