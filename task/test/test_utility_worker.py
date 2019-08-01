from unittest.mock import patch

from celery.exceptions import Retry, MaxRetriesExceededError

from task.test.base import BaseTestCase

from app.api import db
from app.api.models import *

from task.utility.tasks import UtilityTask

class TestUtilityWorker(BaseTestCase):
    """ Test Class for Utility Worker """
    
    def test_push_notification(self):
        """ test function that push notification in the background """
        # first create a dummy va first
        # create dummy wallet here
        # create bank here
        wallet = Wallet()
        db.session.add(wallet)
        db.session.commit()

        transaction_type = TransactionType.query.filter_by(key="TOP_UP").first()

        credit_trx = Transaction(
            wallet_id=wallet.id,
            amount=100,
            notes="some notes",
            transaction_type=transaction_type
        )
        db.session.add(credit_trx)
        db.session.commit()

        result = UtilityTask().push_notification.apply_async(
            args=[credit_trx.id],
            queue="utility"
        )
