"""
    Quota Services
    ________________
    This is module that serve everything related to Transfer Quota
"""
# pylint: disable=bad-whitespace
# pylint: disable=no-self-use
# pylint: disable=import-error
# pylint: disable=no-name-in-module
# pylint: disable=singleton-comparison
from datetime import datetime, timedelta

from sqlalchemy import func, and_, not_
from sqlalchemy.exc import IntegrityError, OperationalError

from app.api import db

from app.api.serializer import (
    TransactionSchema,
    QuotaSchema
)
# helper
from app.api.utility.utils import validate_uuid
# models
from app.api.models import (
    Wallet,
    Quota,
    QuotaUsage,
    Transaction
)
# config
from app.config import config
# task
from task.quota.tasks import QuotaTask
# http error
from app.lib.http_response import ok, accepted
# const
from app.api.const import ERROR as error_response
# exception
from app.lib.http_error import UnprocessableEntity, RequestNotFound


class QuotaServices:
    """ Quota Services Class"""

    def __init__(self, quota_id=None, wallet_id=None, transaction_id=None):
        # only look up in db when source is set
        if quota_id is not None:
            quota_record = Quota.query.filter_by(id=validate_uuid(quota_id)).first()
            if quota_record is None:
                raise RequestNotFound(
                    error_response["QUOTA_NOT_FOUND"]["TITLE"],
                    error_response["QUOTA_NOT_FOUND"]["MESSAGE"],
                )
            # end if
            self.quota = quota_record
        # end if

        if wallet_id is not None:
            wallet_record = Wallet.query.filter_by(id=validate_uuid(wallet_id)).first()
            if wallet_record is None:
                raise RequestNotFound(
                    error_response["WALLET_NOT_FOUND"]["TITLE"],
                    error_response["WALLET_NOT_FOUND"]["MESSAGE"],
                )
            # end if
            self.wallet = wallet_record
        # end if

        if transaction_id is not None:
            transaction_record = \
                Transaction.query.filter_by(id=validate_uuid(transaction_id)).first()
            if transaction_record is None:
                raise RequestNotFound(
                    error_response["TRANSACTION_NOT_FOUND"]["TITLE"],
                    error_response["TRANSACTION_NOT_FOUND"]["MESSAGE"],
                )
            # end if
            self.transaction = transaction_record
        # end if

    def add(self, quota_type=None, no_of_transactions=None, reward_type=None,
            reward_amount=None, is_custom=True):
        """
            function to create quota for one wallet
        """

        if is_custom is False:
            quota_type, no_of_transactions, reward_type, reward_amount = \
                Quota.lookup_current_reward()


        # we add quota to all wallet that active
        # and doesnt have valid quota yet
        start_valid, end_valid = Quota().get_valid_range(quota_type)
        quota = Quota(
            quota_type=quota_type,
            wallet_id=self.wallet.id,
            no_of_transactions=no_of_transactions,
            reward_type=reward_type,
            reward_amount=reward_amount,
            start_valid=start_valid,
            end_valid=end_valid,
        )
        db.session.add(quota)
        db.session.commit()

        response = QuotaSchema(exclude=("used", "remaining")).dump(quota).data
        return response

    def check(self):
        """
            function to query is now this wallet have valid quota
        """
        # get remaining quota here
        quota = Quota.query.filter(
            Quota.wallet_id == self.wallet.id,
            Quota.start_valid <= datetime.utcnow(),
            Quota.end_valid >= datetime.utcnow()
        ).first()

        response = {
            "id": quota.id,
            "remaining": quota.remaining,
            "used": quota.used,
        }
        # set quota id
        self.quota = quota
        return response

    def calculate_reward(self):
        """
            function to generate how much reward that user get based on
            transaction that he made
        """
        # get reward defined in quota
        # 0 means fixed 1 means percentage
        reward_amount = self.quota.reward_amount

        if self.quota.reward_type == 1:
            reward_amount = self.transaction.amount \
                * (self.quota.reward_amount / 100)
        return reward_amount

    def apply_usage(self, usage):
        """ apply quota usage """
        quota_usage = QuotaUsage(
            quota_id=self.quota.id,
            transaction_id=self.transaction.id,
            usage=usage
        )
        db.session.add(quota_usage)
        db.session.commit()
        # actually apply the quota through worker
        QuotaTask().apply.apply_async(
            args=[quota_usage.id], queue="quota"
        )
        return quota_usage

    def revert_usage(self):
        """ apply - / + quota usage to quota """
        # get original quota usage
        quota_usage = QuotaUsage.query.filter_by(
            transaction_id=self.transaction.id
        ).first()
        # set quota id so we can deduct it!
        self.quota = Quota.query.filter_by(id=quota_usage.quota_id).first()
        self.apply_usage(abs(quota_usage.usage))

    def use_quota(self, usage=-1):
        """
            determine whether this transaction valid for reward and if its we
        """
        # fist we need to check whether the wallet have enough quota
        # if enough we generate reward according to business rules
        # if not we return some information that identify he's not get rewarded
        # and not getting any amount
        response = {
            "is_rewarded": False,
            "reward_amount": 0
        }

        quota = self.check()
        if quota["remaining"] > 0:
            self.apply_usage(usage)
            response["reward_amount"] = self.calculate_reward()
            response["is_rewarded"] = True
        return response
