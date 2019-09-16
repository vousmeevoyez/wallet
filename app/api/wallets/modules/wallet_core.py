"""
    Transfer Services
    _________________
    this is module that serve request from wallet transfer :w
    routes
"""
# pylint: disable=no-self-use
# pylint: disable=import-error
# pylint: disable=bad-whitespace
# pylint: disable=invalid-name
# models
from app.api.models import *

# exceptions
from app.api.error.http import *

# error
from app.api.error.message import RESPONSE as error_response

# utility
from app.api.utility.utils import validate_uuid


class WalletCore:
    """ Wallet Core Class """

    def __init__(self, source=None, pin=None, destination=None):
        if source is not None:
            # only look up in db when source is set
            source_wallet = Wallet.query.filter_by(id=validate_uuid(source)).first()
            if source_wallet is None:
                raise RequestNotFound(
                    error_response["WALLET_NOT_FOUND"]["TITLE"],
                    error_response["WALLET_NOT_FOUND"]["MESSAGE"],
                )
            # end if

            if pin is not None:
                # only look up in db when pin is set
                pin_status = source_wallet.check_pin(pin)
                if pin_status == "INCORRECT":
                    raise UnprocessableEntity(
                        error_response["INCORRECT_PIN"]["TITLE"],
                        error_response["INCORRECT_PIN"]["MESSAGE"],
                    )
                elif pin_status == "MAX_ATTEMPT":
                    raise UnprocessableEntity(
                        error_response["MAX_PIN_ATTEMPT"]["TITLE"],
                        error_response["MAX_PIN_ATTEMPT"]["MESSAGE"],
                    )
                elif pin_status == "LOCKED":
                    raise UnprocessableEntity(
                        error_response["WALLET_LOCKED"]["TITLE"],
                        error_response["WALLET_LOCKED"]["MESSAGE"],
                    )
                # end if
            self.source = source_wallet
        # end if

        if destination is not None:
            destination_wallet = Wallet.query.filter_by(
                id=validate_uuid(destination)
            ).first()
            if destination_wallet is None:
                raise RequestNotFound(
                    error_response["WALLET_NOT_FOUND"]["TITLE"],
                    error_response["WALLET_NOT_FOUND"]["MESSAGE"],
                )
            # end if

            if destination_wallet.is_unlocked() is False:
                raise UnprocessableEntity(
                    error_response["WALLET_LOCKED"]["TITLE"],
                    error_response["WALLET_LOCKED"]["MESSAGE"],
                )
            # end if

            if destination_wallet == source_wallet:
                raise UnprocessableEntity(
                    error_response["INVALID_DESTINATION"]["TITLE"],
                    error_response["INVALID_DESTINATION"]["MESSAGE"],
                )
            # end if
            # set attributes here
            self.destination = destination_wallet
        # end if

    # end def


# end class
