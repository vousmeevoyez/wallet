"""
    Withdraw Services Class
    _______________________
    Handle withdraw request process
"""
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError
# db
from app.api import db
# services
from app.api.virtual_accounts.modules.va_services import VirtualAccountServices
# core
from app.api.wallets.modules.wallet_core import WalletCore
# models
from app.api.models import *
# http
from app.api.http_response import *
# exceptions
from app.api.error.http import *

class WithdrawServices(WalletCore):
    """ class that handle request to withdraw """

    def request(self, params):
        """ handle withdraw request """
        amount = float(params["amount"])
        bank_name = params["bank_name"]

        if amount == 0:
            amount = self.source.balance

        if amount < float(self.wallet_config["MINIMAL_WITHDRAW"]):
            raise UnprocessableEntity(self.error_response["MIN_WITHDRAW"]["TITLE"],
                                      self.error_response["MIN_WITHDRAW"]["MESSAGE"])
        #end if

        if amount > float(self.wallet_config["MAX_WITHDRAW"]):
            raise UnprocessableEntity(self.error_response["MAX_WITHDRAW"]["TITLE"],
                                      self.error_response["MAX_WITHDRAW"]["MESSAGE"])
        #end if

        if amount > float(self.source.balance):
            raise UnprocessableEntity(self.error_response["INSUFFICIENT_BALANCE"]["TITLE"],
                                      self.error_response["INSUFFICIENT_BALANCE"]["MESSAGE"])
        #end if

        # before creating a cardless va, we need to make sure there's no ongoing withdraw request
        pending_withdraw = Withdraw.query.filter(Withdraw.wallet_id ==
                                                 self.source.id,
                                                 Withdraw.valid_until > datetime.now()).count()
        if pending_withdraw > 0:
            raise UnprocessableEntity(self.error_response["PENDING_WITHDRAW"]["TITLE"],
                                      self.error_response["PENDING_WITHDRAW"]["MESSAGE"])
        #end if

        # creating withdraw record and set it to valid for certain period of time
        valid_until = datetime.now() + \
        timedelta(minutes=VIRTUAL_ACCOUNT_CONFIG["BNI"]["DEBIT_VA_TIMEOUT"])

        withdraw = Withdraw(
            wallet_id=self.source.id,
            valid_until=valid_until,
        )
        db.session.add(withdraw)
        db.session.commit()

        # define payload here
        va_payload = {
            "bank_name" : "BNI",
            "type"      : "DEBIT",
            "wallet_id" : self.source.id,
            "amount"    : amount
        }

        # GET BANK INFORMATION HERE
        keyword = "%{}%".format(bank_name)
        bank = Bank.query.filter(Bank.name.like(keyword)).first()

        # check va record first make sure no va on the same bank with the same
        # type existed
        va_type = VaType.query.filter_by(key="DEBIT").first()

        va_record = \
        VirtualAccount.query.filter_by(wallet_id=self.source.id,
                                       bank_id=bank.id,
                                       va_type_id=va_type.id).first()
        # if va not existed create va debit
        if va_record is None:
            # create va object here
            virtual_account = VirtualAccount(
                name=self.source.user.name,
            )
            va_response = VirtualAccountServices().add(virtual_account, va_payload)
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
