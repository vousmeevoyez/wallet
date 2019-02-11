"""
    This is Celery Task to help interacting with Bank API
    in the background
"""
from worker import celery

from app.api.models import *

from .BNI.helper import VirtualAccount as VaServices

@celery.task(bind=True)
def create_va(self, virtual_account_id):
    """ create task in background to create a Virtual account """
    # fetch va object
    virtual_account = VirtualAccount.query.filter_by(id=virtual_account_id).first()

    va_payload = {
        "virtual_account" : virtual_account.id,
        "transaction_id"  : virtual_account.trx_id,
        "amount"          : virtual_account.trx_amount,
        "customer_name"   : virtual_account.name,
        "customer_phone"  : "",
        "datetime_expired": virtual_account.datetime_expired,
    }
    resources = virtual_account.va_type.key

    result = VaServices().create_va(resources, va_payload)
    print(result)
