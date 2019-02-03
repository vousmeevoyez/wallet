"""
    Wallet Decorator
    ________________
"""
from functools import wraps

from app.api.http_response import request_not_found

from app.api.models import Wallet

def wallet_exist(f):
    """ ensure wallet entity must be exist """
    @wraps(f)
    def wrapper(*args, **kwargs):
        print(**kwargs)
        '''
        wallet = Wallet.query.filter_by(id=params["wallet_id"]).first()
        if wallet is None:
            return request_not_found()
        '''
        return f(*args, **kwargs)
    return wrapper
#end def
