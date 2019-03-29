"""
    Test Notification services
"""
from datetime import datetime
from unittest.mock import Mock, patch
import requests

from app.test.base import BaseTestCase

from app.api.utility.modules.notif_services import NotifServices

class TestNotificationServices(BaseTestCase):
    """ Test Class for SMS helper"""

    @patch("requests.post")
    def test_post_success(self, mock_post):
        """ test method to post to some rest api and then return successfull request """
        payload = {
            "wallet_id": "1b5af355-72bb-4874-bf33-8e43088a3eb4",
            "created_at": "2019-03-26 10:00:00",
            "amount": 1000,
            "type": "top_up",
            "message": "Top Up Virtual account 10.000"
        }

        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200

        result = NotifServices()._post(payload)
        self.assertTrue(result)

    def test_convert_type(self):
        result = NotifServices()._convert_type("TOP_UP")
        self.assertEqual(result, "top_up")

        result = NotifServices()._convert_type("TRANSFER_OUT")
        self.assertEqual(result, "withdraw_to_bank")

    def test_convert_date(self):
        result = NotifServices()._convert_date(datetime.utcnow())
        self.assertTrue(result)

    def test_send(self):
        data = {
            "wallet_id"        : "some_wallet_id",
            "amount"           : 1000,
            "transaction_type" : "TOP_UP",
            "notes"            : "some message",
        }
        result = NotifServices().send(data)
        self.assertTrue(result)
