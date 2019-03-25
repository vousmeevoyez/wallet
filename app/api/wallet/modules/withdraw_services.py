"""
    Withdraw Services Class
    _______________________
    Handle withdraw request process
"""
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError

from app.api import db
# services
from app.api.virtual_account.modules.va_services import VirtualAccountServices
# models
from app.api.models import *
# http response
from app.api.error.http import *
# configuration
from app.config import config
# utility
from app.api.utility.utils import validate_uuid
# http
from app.api.http_response import *

TRANSACTION_NOTES = config.Config.TRANSACTION_NOTES
WALLET_CONFIG = config.Config.WALLET_CONFIG
VIRTUAL_ACCOUNT_CONFIG = config.Config.VIRTUAL_ACCOUNT_CONFIG
STATUS_CONFIG = config.Config.STATUS_CONFIG
ERROR_CONFIG = config.Config.ERROR_CONFIG

class WithdrawServices:
    """ class that handle request to withdraw """
    def __init__(self, wallet_id, pin):
        wallet_record = Wallet.query.filter_by(id=validate_uuid(wallet_id),
                                               status=STATUS_CONFIG["ACTIVE"]).first()
        if wallet_record is None:
            raise RequestNotFound(ERROR_CONFIG["WALLET_NOT_FOUND"]["TITLE"],
                                  ERROR_CONFIG["WALLET_NOT_FOUND"]["MESSAGE"])
        #end if

        pin_status = wallet_record.check_pin(pin)
        if pin_status == "INCORRECT":
            raise UnprocessableEntity(ERROR_CONFIG["INCORRECT_PIN"]["TITLE"],
                                      ERROR_CONFIG["INCORRECT_PIN"]["MESSAGE"])
        elif pin_status == "MAX_ATTEMPT":
            raise UnprocessableEntity(ERROR_CONFIG["MAX_PIN_ATTEMPT"]["TITLE"],
                                      ERROR_CONFIG["MAX_PIN_ATTEMPT"]["MESSAGE"])
        #end if

        self.va_type = VaType.query.filter_by(key="DEBIT").first()
        self.wallet = wallet_record

    def request(self, params):
        """ handle withdraw request """
        amount = float(params["amount"])
        bank_name = params["bank_name"]

        if amount == 0:
            amount = self.wallet.balance

        if amount < float(WALLET_CONFIG["MINIMAL_WITHDRAW"]):
            raise UnprocessableEntity(ERROR_CONFIG["MIN_WITHDRAW"]["TITLE"],
                                      ERROR_CONFIG["MIN_WITHDRAW"]["MESSAGE"])
        #end if

        if amount > float(WALLET_CONFIG["MAX_WITHDRAW"]):
            raise UnprocessableEntity(ERROR_CONFIG["MAX_WITHDRAW"]["TITLE"],
                                      ERROR_CONFIG["MAX_WITHDRAW"]["MESSAGE"])
        #end if

        if amount > float(self.wallet.balance):
            raise UnprocessableEntity(ERROR_CONFIG["INSUFFICIENT_BALANCE"]["TITLE"],
                                      ERROR_CONFIG["INSUFFICIENT_BALANCE"]["MESSAGE"])
        #end if

        # before creating a cardless va, we need to make sure there's no ongoing withdraw request
        pending_withdraw = Withdraw.query.filter(Withdraw.wallet_id == self.wallet.id,
                                                 Withdraw.valid_until > datetime.now()).count()
        if pending_withdraw > 0:
            raise UnprocessableEntity(ERROR_CONFIG["PENDING_WITHDRAW"]["TITLE"],
                                      ERROR_CONFIG["PENDING_WITHDRAW"]["MESSAGE"])
        #end if

        # creating withdraw record and set it to valid for certain period of time
        valid_until = datetime.now() + \
        timedelta(minutes=VIRTUAL_ACCOUNT_CONFIG["BNI"]["DEBIT_VA_TIMEOUT"])

        withdraw = Withdraw(
            wallet_id=self.wallet.id,
            valid_until=valid_until,
        )
        db.session.add(withdraw)
        db.session.commit()

        # define payload here
        va_payload = {
            "bank_name" : "BNI",
            "type"      : "DEBIT",
            "wallet_id" : self.wallet.id,
            "amount"    : amount
        }

        # GET BANK INFORMATION HERE
        keyword = "%{}%".format(bank_name)
        bank = Bank.query.filter(Bank.name.like(keyword)).first()

        # check va record first make sure no va on the same bank with the same
        # type existed
        va_record = \
        VirtualAccount.query.filter_by(wallet_id=self.wallet.id,
                                       bank_id=bank.id,
                                       va_type_id=self.va_type.id).first()
        # if va not existed create va debit
        if va_record is None:
            # create va object here
            virtual_account = VirtualAccount(
                name=self.wallet.user.name,
            )
            va_response = VirtualAccountServices.add(virtual_account, va_payload)
            va_response = va_response[0]["data"]
        else:
        # update va here
            va_response =\
            VirtualAccountServices(va_record.account_no).reactivate(va_payload)
        #end if
        response = {
            "virtual_account" : va_response["virtual_account"],
            "valid_until"     : va_response["valid_until"],
            "amount"          : va_response["amount"]
        }
        return ok(response)
    #end def
#end class
