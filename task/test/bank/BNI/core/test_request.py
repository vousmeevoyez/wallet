"""
    Remote Call
    ______________
"""
from unittest.mock import Mock, patch

from task.test.base import BaseTestCase

from task.bank.BNI.core.request import BNIOpgAuthRequest, BNIOpgRequest


class TestBNIOpgAuthRequest(BaseTestCase):

    def test_create_signature(self):
        url = "https://apidev.bni.co.id:8066/api/oauth/token"
        http_request = BNIOpgAuthRequest(url=url, method="POST")
        result = http_request.create_signature({
            "accountNo": "0115476151",
            "clientId": "IDBNITU9EQU5B"
        })
        self.assertTrue(len(result) > 15)
    
    def test_to_representation(self):
        url = "https://apidev.bni.co.id:8066/api/oauth/token"
        payload = {"grant_type": "client_credentials"}
        http_request = BNIOpgAuthRequest(url=url, method="POST")
        http_request.payload = payload

        expected_result = {'url': 'https://apidev.bni.co.id:8066/api/oauth/token', 'method': 'POST', 'data': {'grant_type': 'client_credentials', 'clientId': 'IDBNITU9EQU5B', 'signature': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJncmFudF90eXBlIjoiY2xpZW50X2NyZWRlbnRpYWxzIiwiY2xpZW50SWQiOiJJREJOSVRVOUVRVTVCIn0.hJ1y3ychGN-I2KIA2CFqzcOXxmR2hFNk-XxvVD8SIuI'}, 'headers': {'Authorization': 'Basic MDQxYzc0MTQtMDBmZS00MzM4LTk4YWEtYjkwNWFiNWMyOTcyOjg5NGZlMjA5LTRjNzgtNGMyMi05OTI1LWEyM2JhMzY0ODNmMA==', 'Content-Type': 'application/x-www-form-urlencoded'}, 'timeout': 5}
        self.assertEqual(http_request.to_representation(), expected_result)

class TestBNIOpgRequest(BaseTestCase):
    def test_to_representation(self):
        url = "https://apidev.bni.co.id:8066//H2H/v2/getbalance"
        payload = {"accountNo": "123456"}

        http_request = BNIOpgRequest(url=url, method="POST")
        http_request.payload = payload
        # suppose to be json for data
        expected_result = {'url': 'https://apidev.bni.co.id:8066//H2H/v2/getbalance', 'method': 'POST', 'data': '{"accountNo": "123456", "clientId": "IDBNITU9EQU5B", "signature": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhY2NvdW50Tm8iOiIxMjM0NTYiLCJjbGllbnRJZCI6IklEQk5JVFU5RVFVNUIifQ.vBrJS0GqaWu5_chfmftHwXIprXWcLS3MNTuaMk1DfMg"}', 'headers': {'x-api-key': '09ea583b-6d13-47ed-b675-9648f27826f2', 'Content-Type': 'application/json'}, 'timeout': 5}
        self.assertEqual(http_request.to_representation(), expected_result)
