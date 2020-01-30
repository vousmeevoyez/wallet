"""
    This is Celery Task to help interacting with Bank API
    in the background
"""
from datetime import datetime
from celery.signals import task_postrun
from sqlalchemy.exc import OperationalError, IntegrityError

from app.lib.task import BaseTask
from app.api import (
    celery,
    db
)

from app.api.models import (
    Transaction,
    Payment,
    Log,
    Wallet
)
from app.api.utility.utils import backoff

# const
from app.api.const import TRANSACTION_LOG, PAYMENT_STATUS, WORKER

now = datetime.utcnow()


class TransferFailed(Exception):
    """ raised when something occured on transfer process """


@task_postrun.connect
def close_session(*args, **kwargs):
    db.session.remove()


class TransactionTask(BaseTask):
    """Abstract base class for all tasks in my app."""

    @celery.task(
        bind=True,
        max_retries=WORKER["MAX_RETRIES"],
        task_soft_time_limit=WORKER["SOFT_LIMIT"],
        task_time_limit=WORKER["SOFT_LIMIT"],
        acks_late=WORKER["ACKS_LATE"],
    )
    def transfer(self, payment_id):
        """ create task in background to move money between wallet """
        # fetch payment record that going to be processed
        payment = Payment.query.filter_by(id=payment_id).first()
        if payment is None:
            # should abort the transfer
            print("payment not found")

        log = Log.query.filter_by(payment_id=payment.id).first()
        if log is None:
            # create log object if its not exist
            log = Log(payment_id=payment_id)
            db.session.add(log)
        # end if

        transaction = Transaction.query.filter_by(payment_id=payment.id).first()
        if transaction is None:
            # should abort the transfer
            print("transaction not found")
        # end if

        # update log state here
        log.state = 1  # PENDING
        log.created_at = now

        db.session.begin(nested=True)
        try:
            # fetch target wallet here
            if payment.payment_type is True:  # CREDIT
                wallet_id = payment.to
            else:  # DEBIT
                wallet_id = payment.source_account

            wallet = Wallet.query.filter_by(id=wallet_id).with_for_update().first()

            # add wallet balance
            wallet.add_balance(payment.amount)

            payment.status = PAYMENT_STATUS["DONE"]
            log.state = 2  # COMPLETED
            log.created_at = now

            # added transaction balance
            transaction.balance = wallet.balance
            # commit everything here
            db.session.commit()
        except (IntegrityError, OperationalError) as error:
            db.session.rollback()
            payment.status = PAYMENT_STATUS["CANCELLED"]
            # retry the task again
            self.retry(countdown=backoff(self.request.retries), exc=error)
        # end try
        db.session.commit()
        return transaction.id
