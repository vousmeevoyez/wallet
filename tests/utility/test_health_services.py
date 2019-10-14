"""
    Test Health Services
"""
from unittest.mock import Mock, patch

from sqlalchemy.exc import SQLAlchemyError

from app.api.utility.modules.health_services import HealthServices


def test_check_db_success():
    """ test check db successfully check health """
    result = HealthServices._check_db()
    assert result


@patch("flask_sqlalchemy._QueryProperty.__get__")
def test_check_db_failed(mock_model):
    """ test check db failure to check health """
    mock_model.side_effect = SQLAlchemyError("test", "test", "test")
    result = HealthServices._check_db()
    assert result is False

#@patch.object(HealthServices, "task")
#def test_convert_state_to_bool():
#    fake_task = Mock(completed_count=)
#    result = HealthServices._convert_state_to_bool(fake_task)
#    .assertTrue(result)

#    fake_task = Mock(state="FAILED")
#    result = HealthServices._convert_state_to_bool(fake_task)
#    .assertFalse(result)


def test_convert_http_to_bool():
    result = HealthServices._convert_http_to_bool(200)
    assert result

    result = HealthServices._convert_http_to_bool(500)
    assert result is False


def test_convert_to_percentage():
    health_status = {'db': True, 'worker': {'TransactionTask': False, 'BankTask': False, 'PaymentTask': False, 'UtilityTask': False}, 'external': {'BNIVirtualAccount': True, 'BNICoreBank': False}}
    result = HealthServices()._convert_to_percentage(health_status)
    assert result == 28.6


def test_check_worker_success():
    expected_result = False
    worker_status = HealthServices()._check_worker()
    assert worker_status == expected_result


@patch.object(HealthServices, "_check_db")
@patch.object(HealthServices, "_check_worker")
def test_check_partial_success(mock_db, mock_worker):
    mock_db.return_value = True
    mock_worker.return_value = {
        "TransactionTask": True,
        "BankTask": True,
        "PaymentTask": True,
        "UtilityTask": True
    }

    result = HealthServices().check()
    assert result["hp"] == 100
