"""
    This is Celery Task to help interacting with Bank API
    in the background
"""
from worker import celery

from app.api.models import *

from app.api.bank.handler import BankHandler

@celery.task(bind=True)
def create_va(self, virtual_account_id):
    """ create task in background to create a Virtual account """
    # access va data first
    result = BankHandler("BNI").dispatch("CREATE_VA", va_payload)
    print(result)

    payload = {
        "transaction_id" : None,
        "amount"         : None,
        "customer_name"  : None,
        "customer_phone" : None,
        "virtual_account_id" : None,
        "datetime_expired"   : None,
    }

    virtual_account = \
    VirtualAccount.query.filter_by(id=virtual_account_id).first()
    print(virtual_account)
