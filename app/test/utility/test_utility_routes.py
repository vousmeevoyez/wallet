"""
    Test Utility Routes
"""
from unittest.mock import Mock, patch

from app.api.models import *
from app.test.base import BaseTestCase

# mock all response incoming from user services
from app.api.utility.modules.health_services import HealthServices

BASE_URL = "/api/v1"
RESOURCE = "/utility/"

class TestUtilityRoutes(BaseTestCase):
    """ Test Class for User Routes"""

    """
        TEST BEGIN HERE
    """
    def test_health_check_partial_success(self):
        """ test api call for checking health and return partial success"""
        expected_result = {
            'db': True,
            'worker': False,
            'external': {
                'BNIVirtualAccount': True,
                'BNICoreBank': False
            }, 'hp': 50
        }

        result = self.health_check()
        response = result.get_json()
        self.assertEqual(response, expected_result)

    @patch.object(HealthServices, "check")
    def test_health_check_success(self, mock_service):
        """ test api call for checking health and return success"""
        expected_result = {
            'db': True,
            'worker': {
                'TransactionTask': True,
                'BankTask': True,
                'PaymentTask': True,
                'UtilityTask': True
            },
            'external': {
                'BNIVirtualAccount': True,
                'BNICoreBank': True
            },
            'hp': 100
        }
        mock_service.return_value = expected_result

        result = self.health_check()
        response = result.get_json()
        self.assertEqual(response, expected_result)
