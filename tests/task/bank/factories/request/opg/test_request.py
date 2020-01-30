"""
    Remote Call
    ______________
"""
from task.bank.factories.request.opg.request import BNIOpgAuthRequest, BNIOpgRequest


class TestBNIOpgAuthRequest:
    """ Testing class for BNI OPG Auth Request """

    def test_create_signature(self):
        http_request = BNIOpgAuthRequest()
        http_request.url = "https://apidev.bni.co.id:8066/api/oauth/token"
        http_request.method = "POST"
        result = http_request.create_signature(
            {"accountNo": "0115476151", "clientId": "IDBNITU9EQU5B"}
        )
        assert len(result) > 15

    def test_to_representation(self):
        http_request = BNIOpgAuthRequest()
        http_request.url = "https://apidev.bni.co.id:8066/api/oauth/token"
        http_request.payload = {"grant_type": "client_credentials"}
        http_request.method = "POST"

        request = http_request.to_representation()
        assert request["url"]
        assert request["method"]
        assert request["data"]
        assert request["headers"]
        assert request["timeout"]


class TestBNIOpgRequest:
    """ Testing class for BNI OPG Request """

    def test_to_representation(self):
        http_request = BNIOpgRequest()
        http_request.url = "https://apidev.bni.co.id:8066//H2H/v2/getbalance"
        http_request.method = "POST"
        http_request.payload = {"accountNo": "123456"}
        # suppose to be json for data
        request = http_request.to_representation()

        assert request["url"]
        assert request["method"]
        assert request["data"]
        assert request["headers"]
        assert request["timeout"]
