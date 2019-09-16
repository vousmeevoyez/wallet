"""
    This is Celery Task to help interacting with Bank API
    in the background
"""
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from flask import current_app
from app.api import celery, sentry, db

from app.api.models import (
    VirtualAccount,
    VaType,
    Wallet,
    BalanceLog,
    VaLog
)

from task.bank.BNI.va import VirtualAccount as BNIVA
from task.bank.BNI.va import ApiError as BNIVAError

from task.bank.BNI.core import CoreBank as BNICoreBank
from task.bank.BNI.core import ApiError as BNICoreBankError

# services

# config
from app.config.external.bank import BNI_OPG
from app.api.const import WORKER, STATUS, LOGGING


def backoff(attempts):
    """ prevent hammering service with thousand retry"""
    return random.uniform(2, 4) ** attempts


def check_va(va_trx_id):
    # wrapper function to help interact with BNI
    result = None
    try:
        result = BNIVA("CREDIT").get_inquiry(va_trx_id)
    except BNIVAError:
        result = 0
    else:
        # access paymount value
        result = result["payment_amount"]
    # end try
    return result


def count_page(va_count):
    pages = va_count / LOGGING["PAGE_SIZE"]
    if va_count < LOGGING["PAGE_SIZE"]:
        pages = 1
    # end if
    return int(pages)


def record_va(account_no, balance):
    va = VirtualAccount.query.filter_by(account_no=account_no).first()
    # create va log
    log = VaLog(virtual_account_id=va.id, balance=balance)
    db.session.add(log)
    db.session.commit()


class LoggingTask(celery.Task):
    """Abstract base class for all tasks in my app."""

    abstract = True

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Log the exceptions to sentry at retry."""
        sentry.capture_exception(exc)
        super(LoggingTask, self).on_retry(exc, task_id, args, kwargs, einfo)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Log the exceptions to sentry."""
        sentry.capture_exception(exc)
        # end with
        super(LoggingTask, self).on_failure(exc, task_id, args, kwargs, einfo)

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
    def fetch_va(self):
        """ get all virtual account that created on our system and record the
        virtual account balance """
        va_count = VirtualAccount.query.count()
        current_app.logger.info(va_count)
        # after we know how many va we need to split it into pages
        pages = count_page(va_count)

        for page in range(pages):
            # paginate virtual account and process it
            virtual_accounts = VirtualAccount.query.paginate(
                page, LOGGING["PAGE_SIZE"], False
            ).items

            results = []
            with ThreadPoolExecutor(max_workers=4) as executor:
                results = executor.map(
                    check_va, [va.trx_id for va in virtual_accounts]
                )
            # end with

            # zip virtual account with result
            virtual_accounts = zip(virtual_accounts, results)
            for va in virtual_accounts:
                record_va(va[0].account_no, va[1])
            # end for
    # end def

    @celery.task(
        bind=True,
        max_retries=int(WORKER["MAX_RETRIES"]),
        task_soft_time_limit=WORKER["SOFT_LIMIT"],
        task_time_limit=WORKER["SOFT_LIMIT"],
        acks_late=WORKER["ACKS_LATE"],
    )
    def record_external_balance(self):
        """ task to periodically check system balance and external balance is
        match or not"""

        # check system balance
        internal_balance = Wallet.total_balance()
        current_app.logger.info(internal_balance)

        try:
            response = BNICoreBank().get_balance(
                {"account_no": BNI_OPG["MASTER_ACCOUNT"]}
            )
        except BNICoreBankError as error:
            self.retry(countdown=backoff(self.request.retries), exc=error)
        # end try
        else:
            external_balance = response["data"]["bank_account_info"]["balance"]

            balance_log = {
                "account_no": BNI_OPG["MASTER_ACCOUNT"],
                "internal_balance": internal_balance,
                "balance": external_balance,
            }
            external_balance = response["data"]["bank_account_info"]["balance"]
            if internal_balance <= external_balance:
                # we want to keep our external balance more than our internal balance
                balance_log["is_match"] = True
            # end if
            balance_log_records = BalanceLog(**balance_log)
            db.session.add(balance_log_records)
            db.session.commit()
