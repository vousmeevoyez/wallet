"""
    Test Bank Helper
"""
import pytest
from unittest.mock import Mock

from task.bank.lib.helper import opg_extract_error
from task.bank.lib.helper import extract_error


def test_opg_error():
    fake_error = {
        "getInterbankInquiryResponse": {
            "clientId": "BNISERVICE",
            "parameters": {
                "responseCode": "0000",
                "responseMessage": "Error",
                "errorMessage": "Some error message",
                "responseTimestamp": "2017-05-08T14:57:51.963Z",
            },
        }
    }

    fake_exception = Mock()
    fake_exception.original_exception = fake_error

    result = opg_extract_error(fake_exception)
    assert result == "Some error message"


def test_extract_error():
    fake_error = {
        "getInterbankInquiryResponse": {
            "clientId": "BNISERVICE",
            "parameters": {
                "responseCode": "0000",
                "responseMessage": "Error",
                "errorMessage": "Some error message",
                "responseTimestamp": "2017-05-08T14:57:51.963Z",
            },
        }
    }

    fake_exception = Mock()
    fake_exception.original_exception = fake_error

    result = extract_error(fake_exception)
    assert result == "Some error message"
