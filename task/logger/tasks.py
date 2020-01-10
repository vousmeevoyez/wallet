"""
    This is Celery Task to help interacting with Bank API
    in the background
"""
from concurrent.futures import ThreadPoolExecutor

from flask import current_app
from app.api import celery, sentry, db

from app.api.models import (
    VirtualAccount,
    VaType,
    Wallet,
    BalanceLog,
    VaLog
)
from app.api.utility.utils import backoff

from task.bank.factories.provider.factory import generate_provider
from task.bank.lib.provider import ProviderError

# config
from app.config.external.bank import BNI_OPG
from app.api.const import WORKER, LOGGING


def check_va(va_trx_id):
    # wrapper function to help interact with BNI
    result = {
        "amount": 0,
        "status": True
    }
    try:
        provider = generate_provider("BNI_VA")
        provider.set("CREDIT")
        response = provider.get_inquiry(va_trx_id)
    except ProviderError:
        result["status"] = False
    else:
        # access paymount value
        result["amount"] = response["payment_amount"]
    # end try
    return result


def count_page(va_count):
    pages = va_count / LOGGING["PAGE_SIZE"]
    if va_count < LOGGING["PAGE_SIZE"]:
        pages = 1
    # end if
    return int(pages)


def record_va(account_no, balance, status):
    va = VirtualAccount.query.filter_by(account_no=account_no).first()
    # create va log
    log = VaLog(virtual_account_id=va.id, balance=balance, status=status)
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
        current_app.logger.info("No of Virtual Accounts: {}".format(va_count))
        # after we know how many va we need to split it into pages
        pages = count_page(va_count)

        for page in range(pages):
            # paginate virtual account and process it
            virtual_accounts = VirtualAccount.query.join(
                VaType, VirtualAccount.va_type_id == VaType.id
            ).filter(
                VaType.key == "CREDIT"
            ).paginate(
                page, LOGGING["PAGE_SIZE"], False
            ).items

            results = []
            with ThreadPoolExecutor(max_workers=LOGGING["PAGE_SIZE"]) as executor:
                results = executor.map(
                    check_va, [va.trx_id for va in virtual_accounts]
                )
            # end with

            # zip virtual account with result
            virtual_accounts = zip(virtual_accounts, results)
            for va in virtual_accounts:
                record_va(va[0].account_no, va[1]["amount"], va[1]["status"])
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
        current_app.logger.info("Internal balance: {}".format(internal_balance))

        try:
            provider = generate_provider("BNI_OPG")
            response = provider.get_balance(BNI_OPG["MASTER_ACCOUNT"])
        except ProviderError as error:
            self.retry(countdown=backoff(self.request.retries), exc=error)
        # end try
        else:
            external_balance = response["bank_account_info"]["balance"]

            balance_log = {
                "account_no": BNI_OPG["MASTER_ACCOUNT"],
                "internal_balance": internal_balance,
                "balance": external_balance,
            }
            external_balance = response["bank_account_info"]["balance"]
            if internal_balance <= float(external_balance):
                # we want to keep our external balance more than our internal balance
                balance_log["is_match"] = True
            # end if
            balance_log_records = BalanceLog(**balance_log)
            db.session.add(balance_log_records)
            db.session.commit()
