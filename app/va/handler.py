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

    def create_va(self, params):
        payload = {
            'type'            : "createbilling",
            'client_id'       : self.CLIENT_ID,
            'trx_id'          : params["trx_id"],
            'trx_amount'      : params["trx_amount"],
            'billing_type'    : self.BILLING_TYPE,
            'customer_name'   : params["customer_name"],
            'customer_email'  : params["customer_email"] ,
            'customer_phone'  : params["customer_phone"],
            'virtual_account' : params["virtual_account"],
            'datetime_expired': params["datetime_expired"],
            'description'     : params["description"]
        }
        result = self._post(payload)
        return result

    def get_inquiry(self, trx_id):
        payload = {
            'type'     : 'inquirybilling',
            'client_id': self.CLIENT_ID,
            'trx_id'   : trx_id
        }

        result = self._post(payload)
        return result


    def update_balance(self):
        payload = {
            'type'            : 'updatebilling',
            'client_id'       : self.CLIENT_ID,
            'trx_id'          : data.get('trx_id'),
            'trx_amount'      : data.get('trx_amount'),
            'customer_name'   : data.get('customer_name'),
            'customer_email'  : data.get('customer_email') or '',
            'customer_phone'  : data.get('customer_phone') or '',
            'datetime_expired': data.get('datetime_expired') or '',
            'description'     : data.get('description') or ''
        }

        result = self._post(payload)
        return result

