"""
    This is Celery Task to help interacting with various utility
"""
from app.api import (
    celery,
    sentry,
    db
)

from app.api.models import Transaction

from app.api.utility.utils import Notif, backoff, UtilityError

from app.api.const import WORKER


class UtilityTask(celery.Task):
    """Abstract base class for all tasks in my app."""

    abstract = True

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Log the exceptions to sentry at retry."""
        sentry.captureException(exc)
        super(UtilityTask, self).on_retry(exc, task_id, args, kwargs, einfo)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Log the exceptions to sentry."""
        sentry.captureException(exc)
        super(UtilityTask, self).on_failure(exc, task_id, args, kwargs, einfo)

    @celery.task(bind=True)
    def health_check(self, text):
        return text

    """
        PUSH NOTIFICATION
    """

    @celery.task(
        bind=True,
        max_retries=int(WORKER["MAX_RETRIES"]),
        task_soft_time_limit=WORKER["SOFT_LIMIT"],
        task_time_limit=WORKER["SOFT_LIMIT"],
        acks_late=WORKER["ACKS_LATE"],
    )
    def push_notification(self, transaction_id):
        """ create task in background to push some notification """
        # fetch transaction object
        transaction = Transaction.query.filter_by(id=transaction_id).first()

        # build transaction notif payload
        try:
            result = Notif().send(
                {
                    "wallet_id": str(transaction.wallet_id),
                    "amount": transaction.amount,
                    "transaction_type": transaction.transaction_type.key,
                    "balance": transaction.balance,
                    "en_message": transaction.notes,
                }
            )
        except UtilityError as error:
            self.retry(countdown=backoff(self.request.retries), exc=error)
