import pytest

from celery.exceptions import Retry

from unittest.mock import patch

from app.api.models import VaLog, BalanceLog

from task.report.tasks import ReportTask


@patch("task.report.tasks.send_email")
def test_send_report(mock_email, setup_transaction):
    """ test generating report and send it to recipients """
    mock_email.return_value = "OK"

    ReportTask().send_report()


def test_send_report_error(setup_transaction):
    """ test generating report and send it to recipients but it failed"""
    with pytest.raises(Retry):
        ReportTask().send_report()
