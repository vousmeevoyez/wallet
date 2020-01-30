"""
    Test Utility Routes
"""
from unittest.mock import patch

from app.api.utility.modules.health_services import HealthServices

from tests.reusable.api_list import health_check


"""
    TEST BEGIN HERE
"""


def test_health_check_partial_success(client):
    """ test api call for checking health and return partial success"""
    expected_result = {"db": True, "worker": False, "hp": 50.0}

    result = health_check(client)
    response = result.get_json()
    assert response == expected_result


@patch.object(HealthServices, "check")
def test_health_check_success(mock_service, client):
    """ test api call for checking health and return success"""
    expected_result = {
        "db": True,
        "worker": {
            "TransactionTask": True,
            "BankTask": True,
            "PaymentTask": True,
            "UtilityTask": True,
        },
        "hp": 100,
    }
    mock_service.return_value = expected_result

    result = health_check(client)
    response = result.get_json()
    assert response == expected_result
