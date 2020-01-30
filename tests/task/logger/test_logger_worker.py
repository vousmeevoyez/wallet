from unittest.mock import patch

from app.api.models import VaLog, BalanceLog

from task.logger.tasks import LoggingTask


@patch("task.bank.tasks.generate_provider")
def test_fetch_va(mock_provider, setup_credit_va):
    """ test function that transfer money using OPG in the background but
    failed and reach max retries """
    expected_data = {
        "trx_id": "121",
        "virtual_account": "9889909918102605",
        "trx_amount": "1",
        "customer_name": "Jennie",
        "customer_phone": "",
        "customer_email": "",
        "datetime_created": "2018-10-26 06:39:27",
        "expire_date": "2017-10-28 06:39:27",
        "datetime_payment": None,
        "datetime_last_updated": "2018-10-26 06:43:25",
        "payment_ntb": None,
        "payment_amount": "0",
        "va_status": "2",
        "description": "",
        "billing_type": "j",
        "datetime_created_iso8601": "2018-10-26T06:39:27+07:00",
        "expire_date_iso8601": "2017-10-28T06:39:27+07:00",
        "datetime_payment_iso8601": None,
        "datetime_last_updated_iso8601": "2018-10-26T06:43:25+07:00",
    }

    mock_provider.return_value.get_inquiry.return_value = expected_data
    LoggingTask().fetch_va()

    assert VaLog.query.count() == 1


@patch("task.bank.tasks.generate_provider")
def test_record_external_balance(mock_provider, setup_wallet_with_balance):
    """ test background task that periodically check external balance and
    compare it with our internal balance """
    mock_provider.return_value.get_balance.return_value = {
        "account_no": "12345678",
        "internal_balance": "10000",
        "balance": "10000",
    }

    LoggingTask().record_external_balance()
    # must added to make sure the task finished before we end the unittest
    balance_log = BalanceLog.query.filter_by().first()
    assert BalanceLog.query.count() == 1
    assert balance_log.is_match
