""" 
    Test Bank Services
    ___________________
    test bank services module
"""
from unittest.mock import Mock, patch

from app.test.base import BaseTestCase
from app.api.bank.modules.bank_services import BankServices

class TestBankServices(BaseTestCase):
    """ Test Class for Bank Services"""

    def test_get_banks(self):
        """ test function that return all available banks"""
        result = BankServices().get_banks()
        self.assertIsInstance(result["data"], list)
        self.assertTrue(len(result["data"]) > 0)