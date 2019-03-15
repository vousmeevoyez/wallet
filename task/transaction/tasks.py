"""
    This is Celery Task to help interacting with Bank API
    in the background
"""
import random
from datetime import datetime
from celery.signals import task_postrun

from app.api import sentry
from app.api import db

from sqlalchemy.exc import OperationalError, IntegrityError
from app.api import celery

from app.api.models import *

# exceptions
from task.bank.exceptions.general import *

from app.config import config

TRANSACTION_LOG_CONFIG = config.Config.TRANSACTION_LOG_CONFIG
PAYMENT_STATUS_CONFIG = config.Config.PAYMENT_STATUS_CONFIG
WORKER_CONFIG = config.Config.WORKER_CONFIG

now = datetime.utcnow()

@task_postrun.connect
def close_session(*args, **kwargs):
    db.session.remove()

def backoff(attempts):
    """ prevent hammering service with thousand retry"""
    return random.uniform(2,4) ** attempts

class TransferFailed(Exception):
    """ raised when something occured on transfer process """

class TransactionTask(celery.Task):
    """Abstract base class for all tasks in my app."""

    abstract = True

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Log the exceptions to sentry at retry."""
        sentry.captureException(exc)
        super(TransactionTask, self).on_retry(exc, task_id, args, kwargs, einfo)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Log the exceptions to sentry."""
        sentry.captureException(exc)
        super(TransactionTask, self).on_failure(exc, task_id, args, kwargs, einfo)

    @celery.task(bind=True,
                 max_retries=WORKER_CONFIG["MAX_RETRIES"],
                 task_soft_time_limit=WORKER_CONFIG["SOFT_LIMIT"],
                 task_time_limit=WORKER_CONFIG["SOFT_LIMIT"],
                 acks_late=WORKER_CONFIG["ACKS_LATE"],
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
        #end if

        # update log state here
        log.state = 1 # PENDING
        log.created_at = now

        db.session.begin(nested=True)
        try:
            # fetch target wallet here
            if payment.payment_type is True: # CREDIT
                wallet_id = payment.to
            else: # DEBIT
                wallet_id = payment.source_account

            wallet = \
            Wallet.query.filter_by(id=wallet_id).with_for_update().first()

            # add wallet balance
            wallet.add_balance(payment.amount)

            payment.status = PAYMENT_STATUS_CONFIG["DONE"]
            log.state = 2 # COMPLETED
            log.created_at = now
            # commit everything here
            db.session.commit()
        except (IntegrityError, OperationalError) as error:
            db.session.rollback()
            payment.status = PAYMENT_STATUS_CONFIG["CANCELLED"]
            # retry the task again
            self.retry(countdown=backoff(self.request.retries), exc=error)
        #end try
        db.session.commit()
    #end def
