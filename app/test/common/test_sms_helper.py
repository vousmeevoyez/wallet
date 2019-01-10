""" 
    Test SMS Helper
"""
from unittest.mock import Mock, patch
from app.test.base import BaseTestCase
from app.api.common.helper import SmsHelper

class TestSMSHelper(BaseTestCase):

    @patch("requests.post")
    def test_post(self, mock_post):
        payload = {"data" : "Some payload"}

        expected_value = {"data" : "some data"}

        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200

        result = SmsHelper()._post(payload)
        self.assertEqual(result, "REQUEST_SUCCESS")
