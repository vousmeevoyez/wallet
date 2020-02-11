from freezegun import freeze_time
from datetime import datetime

from app.api import db
from app.api.models import Wallet, Quota, QuotaUsage
from app.api.quotas.modules.quota_services import QuotaServices


@freeze_time("2019-01-02")
def test_add_monthly_quota():
    """ case 1: add wallet with monthly transfer quotas """
    wallet = Wallet()
    db.session.add(wallet)
    db.session.commit()

    parameters = {
        "no_of_transactions": 3,
        "reward_amount": 3000,
        "reward_type": "FIXED",
        "quota_type": "MONTHLY"
    }
    response = QuotaServices(wallet_id=str(wallet.id)).add(**parameters)
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
    assert wallet_quotas[0].no_of_transactions == 3
    assert wallet_quotas[0].reward_amount == 3000
    assert wallet_quotas[0].start_valid == expected_start_valid
    assert wallet_quotas[0].end_valid == expected_end_valid


@freeze_time("2019-01-03")
def test_add_daily_quota():
    """ case 1: add wallet daily transfer quota """
    wallet = Wallet()
    db.session.add(wallet)
    db.session.commit()

    parameters = {
        "no_of_transactions": 3,
        "reward_amount": 3000,
        "reward_type": "FIXED",
        "quota_type": "DAILY"
    }
    response = QuotaServices(wallet_id=str(wallet.id)).add(**parameters)
    # generated valid date should be 2019-1-1 to 2019-1-31
    expected_start_valid = datetime(
        year=2019, month=1, day=3, hour=0, minute=0, second=0, microsecond=0
    )
    expected_end_valid = datetime(
        year=2019, month=1, day=3, hour=23, minute=59, second=59, microsecond=59
    )
    wallet_quotas = wallet.quotas.all()
    assert len(wallet_quotas) == 1
    assert wallet_quotas[0].quota_type == "DAILY"
    assert wallet_quotas[0].no_of_transactions == 3
    assert wallet_quotas[0].reward_amount == 3000
    assert wallet_quotas[0].start_valid == expected_start_valid
    assert wallet_quotas[0].end_valid == expected_end_valid


def test_check_monthly_quota(setup_wallet_with_quotas):
    """ case 1: check wallet monthly transfer quota """
    wallet = setup_wallet_with_quotas("MONTHLY")
    response = QuotaServices(wallet_id=str(wallet.id)).check()

    assert response["remaining"] == 3
    assert response["used"] == 0
    # need to check used also!


def test_check_daily_quota(setup_wallet_with_quotas):
    """ case 1: check wallet daily transfer quota """
    wallet = setup_wallet_with_quotas("DAILY")
    response = QuotaServices(wallet_id=str(wallet.id)).check()

    assert response["remaining"] == 3
    assert response["used"] == 0
    # need to check used also!


def test_use_monthly_quota(setup_wallet_with_quotas, setup_transaction):
    """ case 1: use wallet monthly transfer quota """
    wallet = setup_wallet_with_quotas("MONTHLY")
    quota_id = wallet.quotas[0].id

    response = QuotaServices(
        wallet_id=wallet.id,
        quota_id=quota_id,
        transaction_id=setup_transaction.id
    ).use_quota()
    # make sure usage is created
    quota = Quota.query.get(quota_id)
    assert len(quota.quota_usages) == 1
    # make sure get correct reward
    assert response["is_rewarded"] is True
    assert response["reward_amount"] == 3500

    quota_usage = QuotaUsage.query.filter_by(transaction_id=setup_transaction.id).first()
    # make sure usage is correct
    assert quota_usage.status == 0  # PENDING
    assert quota_usage.usage == -1 # deducted value


def test_use_daily_quota(setup_wallet_with_quotas, setup_transaction):
    """ case 1: use wallet daily transfer quota """
    wallet = setup_wallet_with_quotas("DAILY")
    quota_id = wallet.quotas[0].id

    response = QuotaServices(
        wallet_id=wallet.id,
        quota_id=quota_id,
        transaction_id=setup_transaction.id
    ).use_quota()
    # make sure usage is created
    quota = Quota.query.get(quota_id)
    assert len(quota.quota_usages) == 1
    # make sure get correct reward
    assert response["is_rewarded"] is True
    assert response["reward_amount"] == 3500
    # make sure usage is correct
    quota_usage = QuotaUsage.query.filter_by(transaction_id=setup_transaction.id).first()
    assert quota_usage.status == 0  # PENDING
    assert quota_usage.usage == -1 # deducted value
