from unittest.mock import patch
from datetime import datetime

from freezegun import freeze_time

from celery.exceptions import Retry, MaxRetriesExceededError

from app.api import db
from app.api.models import Wallet, Quota, QuotaUsage

from task.quota.tasks import QuotaTask


def test_apply_quota_usage(
    setup_wallet_with_quotas, setup_transaction
):
    """ test background task where quota applied """
    # first we need to create quota usage
    wallet = setup_wallet_with_quotas("MONTHLY")

    quota_usage = QuotaUsage(
        quota_id=wallet.quotas[0].id,
        transaction_id=setup_transaction.id,
        usage=-1
    )
    db.session.add(quota_usage)
    db.session.commit()

    QuotaTask().apply(quota_usage.id)
    # make sure quota is deducted
    quota = Quota.query.get(wallet.quotas[0].id)
    assert quota.no_of_transactions == 2

    # make sure usage is COMPLETED
    quota_usage = QuotaUsage.query.get(quota_usage.id)
    assert quota_usage.status == 1


@freeze_time("2019-01-02")
def test_adds_monthly_quota():
    """ case 1: add wallet with monthly transfer quotas """
    wallet = Wallet()
    db.session.add(wallet)
    db.session.commit()

    QuotaTask().generate_monthly_quota()
    # generated valid date should be 2019-1-1 to 2019-1-31
    expected_start_valid = datetime(
        year=2019, month=1, day=1, hour=0, minute=0, second=0, microsecond=0
    )
    expected_end_valid = datetime(
        year=2019, month=1, day=31, hour=23, minute=59, second=59, microsecond=59
    )
    wallet_quotas = wallet.quotas.all()
    assert len(wallet_quotas) == 1
    assert wallet_quotas[0].quota_type == "MONTHLY"
    assert wallet_quotas[0].no_of_transactions == 1
    assert wallet_quotas[0].reward_amount == 3500
    assert wallet_quotas[0].start_valid == expected_start_valid
    assert wallet_quotas[0].end_valid == expected_end_valid
