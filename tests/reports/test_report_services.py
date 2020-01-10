from datetime import datetime

from app.api.reports.modules.report_services import (
    DailyTransactionReport,
    extract_transactions
)

def test_extract_transactions(setup_transaction):
    start_time = datetime.utcnow().replace(hour=0, minute=0)
    end_time = datetime.utcnow().replace(hour=23, minute=59)

    transactions = extract_transactions(start_time, end_time)
    assert transactions

def test_generate_report(setup_transaction):
    start_time = datetime.utcnow().replace(hour=0, minute=0)
    end_time = datetime.utcnow().replace(hour=23, minute=59)

    transactions = extract_transactions(start_time, end_time)
    filename = DailyTransactionReport(transactions).generate()
    assert filename
