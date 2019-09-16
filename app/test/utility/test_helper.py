"""
    TEST Common Helper
"""
from unittest.mock import Mock, patch

from app.test.base import BaseTestCase

from app.api.utility.utils import Sms, QR, Notif

from app.api.utility.modules.sms_services import SmsServices

from app.api.utility.utils import UtilityError


class TestSms(BaseTestCase):
    """ Test class for SMS helper interface """

    def test_send_success(self):
        """ test function that generate sms template and then send the sms"""
        result = Sms().send("6281219644314", "FORGOT_PIN", "1234")

    @patch.object(SmsServices, "_post")
    def test_send_failed_raise_error(self, mock_post):
        """ test function that generate sms template and then send the sms but
        raise error"""
        mock_post.side_effect = UtilityError(Mock())

        with self.assertRaises(UtilityError):
            result = Sms().send("6281219644314", "FORGOT_PIN", "1234")


class TestQR(BaseTestCase):
    """ Test class for generating QR code"""

    def test_generate_qr(self):
        """ test function thtat generate qr code from json"""
        data = {"wallet_id": "123456789", "data": "More Data"}
        result = QR().generate(data)

    def test_read_qr(self):
        """ test function that decrypt and read the qr code"""
        data = {"wallet_id": "123456789", "data": "More Data"}
        encrypted = QR().generate(data)

        result = QR().read(encrypted)
        self.assertEqual(result, data)


class TestNotif(BaseTestCase):
    """ Test class for notification """

    def test_send(self):
        """ test function that will send push notification through utility """
        data = {
            "wallet_id": "d795ce30-3da6-4fb3-be4f-12d1f46a0688",
            "amount": 1000,
            "balance": 1001,
            "transaction_type": "TOP_UP",
            "en_message": "halo ini notifikasi dari kelvin",
        }
        result = Notif().send(data)
        self.assertTrue(result)
