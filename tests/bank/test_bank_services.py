""" 
    Test Bank Services
    ___________________
    test bank services module
"""
from unittest.mock import Mock, patch

from app.api.banks.modules.bank_services import BankServices


def test_get_banks():
    """ test function that return all available banks"""
    result = BankServices().get_banks()
    assert type(result["data"]) == list
    assert len(result["data"]) > 0
