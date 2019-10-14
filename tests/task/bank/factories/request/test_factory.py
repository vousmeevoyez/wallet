"""
    Testing Factory Request
    ______________________
"""
from task.bank.factories.request.factory import generate_request

class TestRequestFactory:
    """ Testing Factory Request Class"""

    def test_create_bni_auth_opg(self):
        request = generate_request("BNI_AUTH_OPG")
        url = "https://apidev.bni.co.id:8066/api/oauth/token"
        method = "POST"
        payload = {"grant_type": "client_credentials"}

        request.url = url
        request.method = method
        request.payload = payload

        assert request.url == url
        assert request.method == method
        assert request.payload == payload

    def test_create_bni_opg(self):
        request = generate_request("BNI_OPG")
        url = "https://apidev.bni.co.id:8066//H2H/v2/getbalance"
        method = "POST"
        payload = {"accountNo": "1233456"}

        request.url = url
        request.method = method
        request.payload = payload

        assert request.url == url
        assert request.method == method
        assert request.payload == payload

    def test_create_bni_va(self):
        http_request = generate_request("BNI_CREDIT_VA")
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
