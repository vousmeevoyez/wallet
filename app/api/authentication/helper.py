"""
	Authentication Helper
"""
from app.api.models     import Wallet
from app.api.http_response     import bad_request
from app.config     import config

RESPONSE_MSG = config.Config.RESPONSE_MSG

class AuthenticationHelper:
    """ this is class for authentication helper """
    @staticmethod
    def check_wallet_permission(user_id, wallet_id):
        """ function to check is the user have access to this wallet or not"""
        result = Wallet.is_owned(user_id, wallet_id)
        if result is not True:
            return bad_request(RESPONSE_MSG["FAILED"]["UNAUTHORIZED_WALLET"])
        return None
    #end def
#end class
