import pytest
from unittest.mock import MagicMock

from app.api.reports.modules.email_services import (
    create_attachment,
    prepare_email,
    send_email,
    EmailError
)

def test_create_attachment():
    result = create_attachment("tests/reports/sample.xls")
    assert result


def test_prepare_email():
    sender = "sender@modana.id"
    to = "to@modana.id"
    subject = "unit test"
    content = {
        "greeting": "some greeting",
        "message": "some message"
    }
    attachment = None
    template = "daily_reports"

    result = prepare_email(
        sender,
        to,
        subject,
        content,
        attachment,
        template
    )
    assert result


def test_send_email():
    recipients = ["kelvin@modana.id", "kelvin111196@gmail.com"]
    subject = "unit test"
    content = {
        "greeting": "some greeting",
        "message": "some message"
    }
    fullpath = "tests/reports/sample.xls"
    template = "daily_reports"

    result = send_email(
        recipients,
        subject,
        content,
        fullpath,
        template
    )
