from app                import create_app, db
from app.models         import User, Wallet
from app.errors         import bad_request, internal_error, request_not_found
from app.config         import config

RESPONSE_MSG = config.Config.RESPONSE_MSG

class AuthenticationHelper:

    def __init__(self):
        pass
    #end def

    def check_wallet_permission(self, user_id, wallet_id):
        result = Wallet.is_owned(user_id, wallet_id)
        if result != True:
            return bad_request(RESPONSE_MSG["UNAUTHORIZED_WALLET"])
        return None
    #end def

#end class
