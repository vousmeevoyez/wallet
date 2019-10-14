"""
    Test Notification services
"""
from datetime import datetime
from unittest.mock import Mock, patch

from app.api.utility.modules.notif_services import NotifServices


@patch("requests.post")
def test_post_success(mock_post):
    """ test method to post to some rest api and then return successfull request """
    payload = {
        "wallet_id": "1b5af355-72bb-4874-bf33-8e43088a3eb4",
        "created_at": "2019-03-26 10:00:00",
        "amount": 1000,
        "balance": 1000,
        "type": "top_up",
        "message": "Top Up Virtual account 10.000",
    }

    mock_post.return_value = Mock()
    mock_post.return_value.status_code = 200

    result = NotifServices()._post(payload)
    assert result


def test_convert_type():
    result = NotifServices()._convert_type("TOP_UP")
    assert result == "top_up"

    result = NotifServices()._convert_type("BANK_TRANSFER")
    assert result == "withdraw_to_bank"


def test_convert_date():
    result = NotifServices()._convert_date(datetime.utcnow())
    assert result


def test_send():
    data = {
        "wallet_id": "some_wallet_id",
        "amount": 1000,
        "balance": 1001,
        "transaction_type": "TOP_UP",
        "en_message": "some message",
    }
    result = NotifServices().send(data)
    assert result


def test_send_real():
    data = {
        "wallet_id": "d795ce30-3da6-4fb3-be4f-12d1f46a0688",
        "amount": 1000,
        "balance": 1001,
        "transaction_type": "TOP_UP",
        "en_message": "halo ini notifikasi dari kelvin",
    }
    result = NotifServices().send(data)
    assert result
