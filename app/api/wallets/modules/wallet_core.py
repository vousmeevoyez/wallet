"""
    Transfer Services
    _________________
    this is module that serve request from wallet transfer :w
    routes
"""
#pylint: disable=no-self-use
#pylint: disable=import-error
#pylint: disable=bad-whitespace
#pylint: disable=invalid-name
#models
from app.api.models import *
# exceptions
from app.api.error.http import *
# configuration
from app.config import config
# utility
from app.api.utility.utils import validate_uuid

class WalletCore:
    """ Wallet Core Class """

    wallet_config = config.Config.WALLET_CONFIG
    error_response = config.Config.ERROR_CONFIG
    virtual_account_config = config.Config.VIRTUAL_ACCOUNT_CONFIG

    def __init__(self, source=None, pin=None, destination=None):
        if source is not None:
            # only look up in db when source is set
            source_wallet = Wallet.query.filter_by(id=validate_uuid(source)).first()
            if source_wallet is None:
                raise RequestNotFound(self.error_response["WALLET_NOT_FOUND"]["TITLE"],
                                      self.error_response["WALLET_NOT_FOUND"]["MESSAGE"])
            #end if

            if pin is not None:
                # only look up in db when pin is set
                pin_status = source_wallet.check_pin(pin)
                if pin_status == "INCORRECT":
                    raise UnprocessableEntity(self.error_response["INCORRECT_PIN"]["TITLE"],
                                              self.error_response["INCORRECT_PIN"]["MESSAGE"])
                elif pin_status == "MAX_ATTEMPT":
                    raise UnprocessableEntity(self.error_response["MAX_PIN_ATTEMPT"]["TITLE"],
                                              self.error_response["MAX_PIN_ATTEMPT"]["MESSAGE"])
                elif pin_status == "LOCKED":
                    raise UnprocessableEntity(self.error_response["WALLET_LOCKED"]["TITLE"],
                                              self.error_response["WALLET_LOCKED"]["MESSAGE"])
                #end if
            self.source = source_wallet
        #end if

        if destination is not None:
            destination_wallet = \
            Wallet.query.filter_by(id=validate_uuid(destination)).first()
            if destination_wallet is None:
                raise RequestNotFound(self.error_response["WALLET_NOT_FOUND"]["TITLE"],
                                      self.error_response["WALLET_NOT_FOUND"]["MESSAGE"])
            #end if

            if destination_wallet.is_unlocked() is False:
                raise UnprocessableEntity(self.error_response["WALLET_LOCKED"]["TITLE"],
                                          self.error_response["WALLET_LOCKED"]["MESSAGE"])
            #end if

            if destination_wallet == source_wallet:
                raise UnprocessableEntity(self.error_response["INVALID_DESTINATION"]["TITLE"],
                                          self.error_response["INVALID_DESTINATION"]["MESSAGE"])
            #end if
            # set attributes here
            self.destination = destination_wallet
        #end if
    #end def
#end class
