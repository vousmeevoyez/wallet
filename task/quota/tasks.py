"""
    This is Celery Task to help interacting with quota
"""
from celery.signals import task_postrun
from sqlalchemy import and_, not_
from sqlalchemy.exc import OperationalError, IntegrityError

from app.lib.task import BaseTask
from app.api import (
    celery,
    sentry,
    db
)

from app.api.models import Wallet, Quota, QuotaUsage

from app.api.utility.utils import (
    backoff,
    UtilityError
)

from app.api.const import WORKER


@task_postrun.connect
def close_session(*args, **kwargs):
    db.session.remove()


class QuotaTask(BaseTask):
    """Abstract base class for all tasks in my app."""

    @celery.task(
        bind=True,
        max_retries=int(WORKER["MAX_RETRIES"]),
        task_soft_time_limit=WORKER["SOFT_LIMIT"],
        task_time_limit=WORKER["SOFT_LIMIT"],
        acks_late=WORKER["ACKS_LATE"],
    )
    def apply(self, quota_usage_id):
        """ apply pending quota usage in background """
        quota_usage = QuotaUsage.query.filter_by(id=quota_usage_id).first()
        if quota_usage is None:
            print("revoke task...")
            celery.control.revoke(self.request.id)

        # begin transaction
        db.session.begin(nested=True)
        try:
            # fetch latest quota = select for update quota balance!
            quota = Quota.query.filter_by(
                id=quota_usage.quota_id
            ).with_for_update().first()
            # latest quota = quota + usage
            quota.no_of_transactions = \
                quota.no_of_transactions + quota_usage.usage
            # update quota usage into completed
            quota_usage.status = 1
            db.session.commit()
        except (IntegrityError, OperationalError) as error:
            db.session.rollback()
            # retry
            self.retry(countdown=backoff(self.request.retries), exc=error)
        else:
            # final commit
            db.session.commit()
        # end try

    @celery.task(
        bind=True,
        max_retries=int(WORKER["MAX_RETRIES"]),
        task_soft_time_limit=WORKER["SOFT_LIMIT"],
        task_time_limit=WORKER["SOFT_LIMIT"],
        acks_late=WORKER["ACKS_LATE"],
    )
    def generate_monthly_quota(self):
        """ generate transfer quota every 1st day of month based on csv """
        quota_type, no_of_transactions, reward_type, reward_amount = \
            Quota.lookup_current_reward()

        # we add quota to all wallet that active
        # and doesnt have valid quota yet
        start_valid, end_valid = Quota().get_valid_range(quota_type)

        wallets = Wallet.query.filter(
            Wallet.status == 1,
            ~Wallet.quotas.any(
                and_(
                    Quota.start_valid <= start_valid,
                    Quota.end_valid >= end_valid
                )
            ),
        ).all()

        quotas = []
        for wallet in wallets:
            quota = Quota(
                quota_type=quota_type,
                wallet_id=wallet.id,
                no_of_transactions=no_of_transactions,
                reward_amount=reward_amount,
                reward_type=reward_type,
                start_valid=start_valid,
                end_valid=end_valid,
            )
            quotas.append(quota)
        # end for
        try:
            db.session.add_all(quotas)
            db.session.commit()
        except (IntegrityError, OperationalError) as error:
            self.retry(countdown=backoff(self.request.retries), exc=error)
