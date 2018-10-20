from app        import db
from app.config import config

from utility import remote_call

BNI_ECOLLECTION_CONFIG = config.Config.BNI_ECOLLECTION_CONFIG

class Handlers(object):

    BASE_URL     = BNI_ECOLLECTION_CONFIG["BASE_URL_DEV"]
    SECRET_KEY   = BNI_ECOLLECTION_CONFIG["SECRET_KEY"]
    CLIENT_ID    = BNI_ECOLLECTION_CONFIG["CLIENT_ID"]
    BILLING_TYPE = BNI_ECOLLECTION_CONFIG["BILLING_TYPE"]

    def _post(self, payload):
        remote_response = remote_call.post( self.BASE_URL, self.CLIENT_ID, self.SECRET_KEY, payload)
        return remote_response

    def create_va(self, trx_id, amount, name, **kwargs):
        payload = {
            'type'            : "createbilling",
            'client_id'       : self.CLIENT_ID,
            'trx_id'          : trx_id,
            'trx_amount'      : amount,
            'billing_type'    : self.BILLING_TYPE,
            'customer_name'   : kwargs.get('customer_name'),
            'customer_email'  : kwargs.get('customer_email') or '',
            'customer_phone'  : kwargs.get('customer_phone') or '',
            'virtual_account' : kwargs.get('virtual_account') or '',
            'datetime_expired': kwargs.get('datetime_expired') or '',
            'description'     : kwargs.get('description') or ''
        }
        result = self._post(payload)
        return result
