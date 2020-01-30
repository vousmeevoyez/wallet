"""
    This is Celery Task to help interacting with Bank API
    in the background
"""
from datetime import datetime, timedelta
from celery.signals import task_postrun

# core
from app.lib.task import BaseTask
from app.api import (
    db,
    celery,
    scheduler
)

# models
from app.api.models import *

# exceptions
from sqlalchemy.exc import OperationalError, IntegrityError
from celery.exceptions import MaxRetriesExceededError
from app.lib.http_error import UnprocessableEntity

# configuration
from app.api.const import BACKGROUND_PAYMENT, WORKER

max_retries = int(BACKGROUND_PAYMENT["DAY"]) / int(BACKGROUND_PAYMENT["COUNTDOWN"])


class PaymentTask(BaseTask):
    """Abstract base class for all tasks in my app."""

    @celery.task(
        bind=True,
        max_retries=max_retries,
        task_soft_time_limit=WORKER["SOFT_LIMIT"],
        task_time_limit=WORKER["SOFT_LIMIT"],
        acks_late=WORKER["ACKS_LATE"],
    )
    def background_transfer(self, plan_id, flag="AUTO_DEBIT"):
        """ create task in background to move money between wallet """
        from app.api.transfer.modules.transfer_services import TransferServices

        # fetch payment record that going to be processed
        # extract all info needed from plan_id
        plan = Plan.query.filter(Plan.id == plan_id, Plan.status.in_([0, 1, 2])).first()
        if plan is None:
            # it means the record already paid need to revoke
            print("revoke task....")
            celery.control.revoke(self.request.id)
            return False
        # end if

        # aggregate amount
        total_amount, plans = PaymentPlan.total(plan)
        # bank account
        destination = plan.payment_plan.destination
        # exchange bank account number with bank account id
        bank_account = BankAccount.query.filter_by(account_no=destination).first()
        source = str(plan.payment_plan.wallet_id)

        # update plan to STARTED
        for plan in plans:
            plan.status = 1
            db.session.commit()
        # end for

        try:
            response = TransferServices(source).external_transfer(
                {
                    "destination": str(bank_account.id),
                    "amount": total_amount,
                    "notes": None,
                },
                flag=flag,
            )
        except UnprocessableEntity as error:
            try:
                # update plan to RETRYING
                for plan in plans:
                    plan.status = 2
                    db.session.commit()
                # end for

                self.retry(
                    countdown=int(BACKGROUND_PAYMENT["COUNTDOWN"]),
                    expires=int(BACKGROUND_PAYMENT["EXPIRES"]),
                )
            except MaxRetriesExceededError:
                # update plan to FAILED
                for plan in plans:
                    plan.status = 4
                    db.session.commit()
                # end for

                # should send queue to try again tomorrow
                print("Max Retry Reached")
                # set schedule for plan
                # the next due date should be current time + 3 seconds
                next_due_date = datetime.utcnow() + timedelta(seconds=5)
                job = scheduler.add_job(
                    PaymentTask.background_transfer.delay,
                    trigger="date",
                    next_run_time=next_due_date,
                    args=[plan.id],
                )
            # end try
        else:
            # update plan to SENDING
            for plan in plans:
                plan.status = 3
                db.session.commit()
            # end for
        # end def
