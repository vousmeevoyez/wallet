"""
    Test SMS Helper
"""
from unittest.mock import Mock, patch
import requests

from app.test.base import BaseTestCase

from app.api.utility.modules.sms_services import SmsServices
from app.api.utility.modules.sms_services import SmsError
from app.api.utility.modules.sms_services import ApiError


def raise_api_error(*args):
    """ function to raise api error """
    raise ApiError


class TestSMSHelper(BaseTestCase):
    """ Test Class for SMS helper"""

    @patch("requests.post")
    def test_post_success(self, mock_post):
        """ test method to post to some rest api and then return successfull request """
        payload = {
            "source": "Developer",
            "destination": "+6512345678",
            "clientMessageId": "MyBd00001",
            "text": "Hello World",
            "encoding": "AUTO",
            "scheduled": "2016-11-03T08:24:20.332Z",
            "expiry": "2016-11-03T18:24:20.332Z",
        }

        api_name = "SEND_SMS_SINGLE"

        expected_value = {
            "umid": "f9eaeb51-24fd-e611-813c-06ed3428fe67",
            "clientMessageId": None,
            "destination": "6512345678",
            "status": {
                "code": "QUEUED",
                "description": "SMS is accepted and queued for processing",
            },
        }

        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        result = SmsServices()._post(api_name, payload)
        self.assertTrue(result)

    @patch("requests.post")
    def test_post_failed(self, mock_post):
        """ test method to post to some rest api but server return 400 """
        payload = {
            "source": "Developer",
            "destination": "+6512345678",
            "clientMessageId": "MyBd00001",
            "text": "Hello World",
            "encoding": "AUTO",
            "scheduled": "2016-11-03T08:24:20.332Z",
            "expiry": "2016-11-03T18:24:20.332Z",
        }

        api_name = "SEND_SMS_SINGLE"

        expected_value = {
            "code": 0,
            "message": "string",
            "errorId": "string",
            "timestamp": "2016-11-28T10:32:42.881Z",
        }

        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 400
        mock_post.return_value.json.return_value = expected_value

        result = SmsServices()._post(api_name, payload)
        self.assertFalse(result)

    @patch("requests.post")
    def test_post_timeout(self, mock_post):
        """ test method to post to some rest api and then raise timeout request """
        payload = {
            "source": "Developer",
            "destination": "+6512345678",
            "clientMessageId": "MyBd00001",
            "text": "Hello World",
            "encoding": "AUTO",
            "scheduled": "2016-11-03T08:24:20.332Z",
            "expiry": "2016-11-03T18:24:20.332Z",
        }

        api_name = "SEND_SMS_SINGLE"

        mock_post.side_effect = requests.exceptions.Timeout

        # make sure the error is raised
        with self.assertRaises(ApiError):
            SmsServices()._post(api_name, payload)

    @patch("requests.post")
    def test_post_unknown(self, mock_post):
        """ test method to post to some rest api and then raise unknown request """
        payload = {
            "source": "Developer",
            "destination": "+6512345678",
            "clientMessageId": "MyBd00001",
            "text": "Hello World",
            "encoding": "AUTO",
            "scheduled": "2016-11-03T08:24:20.332Z",
            "expiry": "2016-11-03T18:24:20.332Z",
        }

        api_name = "SEND_SMS_SINGLE"

        mock_post.side_effect = requests.exceptions.RequestException

        # make sure the error is raised
        with self.assertRaises(ApiError):
            SmsServices()._post(api_name, payload)

    @patch.object(SmsServices, "_post")
    def test_send_sms_success(self, mock_post):
        """ test method to successfully send sms """
        message = {"from": "MODANA_DEV", "text": "some message here"}
        mock_post.return_value = True
        result = SmsServices().send_sms("081212341234", message)
        self.assertTrue(result)

    @patch.object(SmsServices, "_post")
    def test_send_sms_failed(self, mock_post):
        """ test method to send sms but raise some error"""
        message = {"from": "MODANA_DEV", "text": "some message here"}

        mock_post.side_effect = ApiError(Mock())
        # make sure the error is raised
        with self.assertRaises(SmsError):
            SmsServices().send_sms("081212341234", message)

    def test_send_sms_real(self):
        """ test method to send real sms"""
        message = {"from": "MODANA_DEV", "text": "some message here"}

        result = SmsServices().send_sms("6281219644314", message)
        self.assertTrue(result)
