from app.api            import db
from app.api.models     import User, Wallet
from app.api.errors     import bad_request, internal_error, request_not_found
from app.api.config     import config

RESPONSE_MSG = config.Config.RESPONSE_MSG

class AuthenticationHelper:

    def __init__(self):
        pass
    #end def

    def check_wallet_permission(self, user_id, wallet_id):
        result = Wallet.is_owned(user_id, wallet_id)
        if result != True:
            return bad_request(RESPONSE_MSG["FAILED"]["UNAUTHORIZED_WALLET"])
        return None
    #end def

#end class
