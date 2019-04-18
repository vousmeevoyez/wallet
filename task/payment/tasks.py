"""
    This is Celery Task to help interacting with Bank API
    in the background
"""
from datetime import datetime, timedelta
from celery.signals import task_postrun
# core
from app.api import sentry
from app.api import db
from app.api import celery
from app.api import scheduler
# transfer services
from app.api.wallets.modules.transfer_services import TransferServices
# models
from app.api.models import *
# exceptions
from sqlalchemy.exc import OperationalError, IntegrityError
from celery.exceptions import MaxRetriesExceededError
from app.api.error.http import *
# configuration
from app.config import config

BACKGROUND_PAYMENT_CONFIG = config.Config.BACKGROUND_PAYMENT_CONFIG
PAYMENT_STATUS_CONFIG = config.Config.PAYMENT_STATUS_CONFIG
WORKER_CONFIG = config.Config.WORKER_CONFIG

now = datetime.utcnow()

class PaymentTask(celery.Task):
    """Abstract base class for all tasks in my app."""

    abstract = True

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Log the exceptions to sentry at retry."""
        sentry.captureException(exc)
        super(PaymentTask, self).on_retry(exc, task_id, args, kwargs, einfo)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Log the exceptions to sentry."""
        sentry.captureException(exc)
        super(PaymentTask, self).on_failure(exc, task_id, args, kwargs, einfo)

    @celery.task(bind=True,
                 max_retries=BACKGROUND_PAYMENT_CONFIG["MAX_RETRIES"],
                 task_soft_time_limit=WORKER_CONFIG["SOFT_LIMIT"],
                 task_time_limit=WORKER_CONFIG["SOFT_LIMIT"],
                 acks_late=WORKER_CONFIG["ACKS_LATE"],
                )
    def background_transfer(self, plan_id):
        """ create task in background to move money between wallet """
        # fetch payment record that going to be processed
        # extract all info needed from plan_id
        plan = Plan.query.filter_by(id=plan_id).first()
        # aggregate amount
        total_amount = plan.payment_plan.total(datetime.now())
        # payment amoun
        destination = plan.payment_plan.destination
        # exchange bank account number with bank account id
        bank_account = \
        BankAccount.query.filter_by(account_no=destination).first()
        source = str(plan.payment_plan.wallet_id)

        # update plan to STARTED
        plan.status = 1
        db.session.commit()

        try:
            response = TransferServices(source).external_transfer({
                "destination" : str(bank_account.id),
                "amount" : total_amount,
                "notes" : None,
            }, flag="AUTO_DEBIT")
        except UnprocessableEntity as error:
            print(error)
            try:
                # update plan to RETRYING
                plan.status = 2
                db.session.commit()

                self.retry(countdown=BACKGROUND_PAYMENT_CONFIG["COUNTDOWN"])
            except MaxRetriesExceededError:
                # update plan to FAILED
                plan.status = 4
                db.session.commit()
                # should send queue to try again tomorrow
                print("Max Retry Reached")
                # set schedule for plan
                # the next due date should be current time + 3 seconds
                next_due_date = datetime.now() + timedelta(seconds=5)
                job = scheduler.add_job(
                    PaymentTask.background_transfer.delay,
                    trigger='date',
                    next_run_time=next_due_date,
                    args=[plan.id]
                )
            # end try
        else:
            # update plan to SENDING
            plan.status = 3
            db.session.commit()
        # end try
    #end def
