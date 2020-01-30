"""
    Celery task for report
"""
from datetime import datetime

from flask import current_app

from app.lib.task import BaseTask
from app.api import celery, db

from app.api.reports.modules.report_services import (
    extract_transactions,
    DailyTransactionReport
)
from app.api.reports.modules.email_services import (
    send_email,
    EmailError
)
from app.api.utility.utils import backoff

# config
from app.api.const import WORKER, LOGGING, REPORTS


class ReportTask(BaseTask):

    @celery.task(
        bind=True,
        max_retries=int(WORKER["MAX_RETRIES"]),
        task_soft_time_limit=WORKER["SOFT_LIMIT"],
        task_time_limit=WORKER["SOFT_LIMIT"],
        acks_late=WORKER["ACKS_LATE"],
    )
    def send_report(self):
        """ extract all transaction for today, transform it into excel and send
        it via email """
        # set 0.0 - 23.59 as time range
        start_time = datetime.utcnow().replace(hour=0, minute=1)
        end_time = datetime.utcnow().replace(hour=23, minute=59)

        # extract
        transactions = extract_transactions(start_time, end_time)
        # transform
        report_filename = DailyTransactionReport(transactions).generate()
        # send
        subject = "Modanaku Daily Report - {}".format(
            datetime.utcnow().strftime("%Y-%m-%d")
        )
        content = {
            "message": "Dear All, <br> Here's attached daily report of \
                        Modanaku Transactions",
        }

        template_name = "daily_reports"
        try:
            send_email(
                REPORTS["RECIPIENTS"], subject, content, report_filename, template_name
            )
        except EmailError:
            self.retry(backoff=backoff)
