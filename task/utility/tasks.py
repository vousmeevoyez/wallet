"""
    This is Celery Task to help interacting with various utility
"""
from app.lib.task import BaseTask
from app.api import (
    celery,
    db
)

from app.api.models import Transaction

from app.api.utility.utils import Notif, backoff, UtilityError

from app.api.const import WORKER


class UtilityTask(BaseTask):
    """Abstract base class for all tasks in my app."""

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
