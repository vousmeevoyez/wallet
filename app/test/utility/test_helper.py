"""
    TEST Common Helper
"""
from unittest.mock import Mock, patch

from app.test.base import BaseTestCase

from app.api.utility.utils import Sms
from app.api.utility.utils import QR

from app.api.utility.modules.sms_services import SmsServices
from app.api.utility.modules.sms_services import ApiError
from app.api.utility.modules.sms_services import SmsError

class TestSms(BaseTestCase):
    """ Test class for SMS helper interface """

    def test_send_success(self):
        """ test function that generate sms template and then send the sms"""
        result = Sms().send("6281219644314", "FORGOT_PIN", "1234")

    @patch.object(SmsServices, "_post")
    def test_send_failed_raise_error(self, mock_post):
        """ test function that generate sms template and then send the sms but
        raise error"""
        mock_post.side_effect = ApiError(Mock())

        with self.assertRaises(SmsError):
            result = Sms().send("6281219644314", "FORGOT_PIN", "1234")

class TestQR(BaseTestCase):
    """ Test class for generating QR code"""

    def test_generate_qr(self):
        """ test function thtat generate qr code from json"""
        data = {
            "wallet_id" : "123456789",
            "data"      : "More Data",
        }
        result = QR().generate(data)

    def test_read_qr(self):
        """ test function that decrypt and read the qr code"""
        data = {
            "wallet_id" : "123456789",
            "data"      : "More Data",
        }
        encrypted = QR().generate(data)

        result = QR().read(encrypted)
        self.assertEqual(result, data)
