"""
    Test Health Services
"""
from unittest.mock import Mock, patch

from sqlalchemy.exc import SQLAlchemyError

from app.test.base import BaseTestCase

from app.api.utility.modules.health_services import HealthServices

from task.bank.BNI.va import VirtualAccount as BNIVirtualAccount
from task.bank.BNI.va import ApiError as BNIVirtualAccountApiError
from task.bank.BNI.core import CoreBank as BNICoreBank
from task.bank.BNI.core import ApiError as BNICoreBankApiError


class TestHealthServices(BaseTestCase):
    """ Test Class for SMS helper"""

    def test_check_db_success(self):
        """ test check db successfully check health """
        result = HealthServices._check_db()
        self.assertTrue(result)

    @patch("flask_sqlalchemy._QueryProperty.__get__")
    def test_check_db_failed(self, mock_model):
        """ test check db failure to check health """
        mock_model.side_effect = SQLAlchemyError("test", "test", "test")
        result = HealthServices._check_db()
        self.assertFalse(result)

    #@patch.object(HealthServices, "task")
    #def test_convert_state_to_bool(self):
    #    fake_task = Mock(completed_count=)
    #    result = HealthServices._convert_state_to_bool(fake_task)
    #    self.assertTrue(result)

    #    fake_task = Mock(state="FAILED")
    #    result = HealthServices._convert_state_to_bool(fake_task)
    #    self.assertFalse(result)

    def test_convert_http_to_bool(self):
        result = HealthServices._convert_http_to_bool(200)
        self.assertTrue(result)

        result = HealthServices._convert_http_to_bool(500)
        self.assertFalse(result)

    def test_convert_to_percentage(self):
        health_status = {'db': True, 'worker': {'TransactionTask': False, 'BankTask': False, 'PaymentTask': False, 'UtilityTask': False}, 'external': {'BNIVirtualAccount': True, 'BNICoreBank': False}}
        result = HealthServices()._convert_to_percentage(health_status)
        self.assertEqual(result, 28.6)

    def test_check_worker_success(self):
        expected_result = False
        worker_status = HealthServices()._check_worker()
        self.assertEqual(worker_status, expected_result)

    def test_check_external_failed(self):
        expected_result = {'BNIVirtualAccount': False, 'BNICoreBank': False}
        external_status = HealthServices()._check_external()
        self.assertEqual(external_status, expected_result)

    @patch.object(BNIVirtualAccount, "health_check")
    @patch.object(BNICoreBank, "health_check")
    def test_check_external_failed(self, mock_va, mock_core_bank):
        mock_va.return_value = 200
        mock_core_bank.return_value = 200

        expected_result = {'BNIVirtualAccount': True}
        external_status = HealthServices()._check_external()
        self.assertEqual(external_status, expected_result)

    @patch.object(HealthServices, "_check_db")
    @patch.object(HealthServices, "_check_worker")
    @patch.object(HealthServices, "_check_external")
    def test_check_partial_success(self, mock_db, mock_worker, mock_external):
        mock_db.return_value = True
        mock_worker.return_value = {
            "TransactionTask": True,
            "BankTask": True,
            "PaymentTask": True,
            "UtilityTask": True
        }
        mock_external.return_value = {
            "BNIVirtualAccount": True,
        }

        result = HealthServices().check()
        self.assertEqual(result["hp"], 100)
