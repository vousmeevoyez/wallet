"""
    Celery task for report
"""
import os
from datetime import datetime

from flask import current_app
from app.api import celery, sentry, db

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
from app.config.external.bank import BNI_OPG
from app.api.const import WORKER, LOGGING, REPORTS


class ReportTask(celery.Task):
    """Abstract base class for all tasks in my app."""

    abstract = True

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Log the exceptions to sentry at retry."""
        sentry.capture_exception(exc)
        super(ReportTask, self).on_retry(exc, task_id, args, kwargs, einfo)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Log the exceptions to sentry."""
        sentry.capture_exception(exc)
        # end with
        super(ReportTask, self).on_failure(exc, task_id, args, kwargs, einfo)

    @celery.task(bind=True)
    def health_check(self, text):
        return text

    """
        QUERY ALL BNI
    """

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
