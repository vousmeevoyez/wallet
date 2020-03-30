"""
    Withdraw Services Class
    _______________________
    Handle withdraw request process
"""
from datetime import datetime, timedelta

# db
from app.api import db

# services
from app.api.virtual_accounts.modules.va_services import VirtualAccountServices

# core
from app.api.wallets.modules.wallet_core import WalletCore

# models
from app.api.models import Withdraw, Bank, VirtualAccount, VaType

# http
from app.lib.http_response import ok

# const
from app.api.const import STATUS, WALLET, VIRTUAL_ACCOUNT

# exceptions
from app.lib.http_error import UnprocessableEntity

# error
from app.api.const import ERROR as error_response


class WithdrawServices(WalletCore):
    """ class that handle request to withdraw """

    def request(self, params):
        """ handle withdraw request """
        amount = float(params["amount"])
        bank_code = params["bank_code"]

        if amount == 0:
            # ADD RULES HERE
            # if its less than 2.5 jt we use that value but if its more, we use
            # we use debit max balance
            current_balance = self.source.balance
            allowed_max_balance = float(VIRTUAL_ACCOUNT["009"]["DEBIT_MAX_BALANCE"])

            if current_balance < allowed_max_balance:
                amount = current_balance
            else:
                amount = VIRTUAL_ACCOUNT["009"]["DEBIT_MAX_BALANCE"]

        if amount < float(WALLET["MINIMAL_WITHDRAW"]):
            raise UnprocessableEntity(
                error_response["MIN_WITHDRAW"]["TITLE"],
                error_response["MIN_WITHDRAW"]["MESSAGE"],
            )

        if amount > float(WALLET["MAX_WITHDRAW"]):
            raise UnprocessableEntity(
                error_response["MAX_WITHDRAW"]["TITLE"],
                error_response["MAX_WITHDRAW"]["MESSAGE"],
            )

        if amount > float(self.source.balance):
            raise UnprocessableEntity(
                error_response["INSUFFICIENT_BALANCE"]["TITLE"],
                error_response["INSUFFICIENT_BALANCE"]["MESSAGE"],
            )

        # before creating a cardless va, we need to make sure there's no ongoing withdraw request
        pending_withdraw = Withdraw.query.filter(
            Withdraw.wallet_id == self.source.id, Withdraw.valid_until > datetime.now()
        ).count()
        if pending_withdraw > 0:
            raise UnprocessableEntity(
                error_response["PENDING_WITHDRAW"]["TITLE"],
                error_response["PENDING_WITHDRAW"]["MESSAGE"],
            )

        # creating withdraw record and set it to valid for certain period of time
        valid_until = datetime.now() + timedelta(
            minutes=VIRTUAL_ACCOUNT["009"]["DEBIT_VA_TIMEOUT"]
        )

        withdraw = Withdraw(wallet_id=self.source.id, valid_until=valid_until)
        db.session.add(withdraw)
        db.session.commit()

        # ADD RULES HERE
        # if its less than 2.5 jt we use that value but if its more, we use

        # define payload here
        va_payload = {
            "bank_code": bank_code,
            "va_type": "DEBIT",
            "wallet_id": self.source.id,
            "amount": amount,
        }

        # GET BANK INFORMATION HERE
        bank = Bank.query.filter_by(code=bank_code).first()

        # check va record first make sure no va on the same bank with the same
        # type existed
        va_type = VaType.query.filter_by(key="DEBIT").first()

        va_record = VirtualAccount.query.filter_by(
            wallet_id=self.source.id,
            bank_id=bank.id,
            va_type_id=va_type.id,
            status=STATUS["ACTIVE"],
        ).first()
        # if va not existed create va debit
        if va_record is None:
            # create va object here
            va_payload["name"] = self.source.user.name
            va_response = VirtualAccountServices().add(**va_payload)
            va_response = va_response[0]["data"]
        else:
            # update va here
            va_response = VirtualAccountServices(va_record.account_no).reactivate(
                **va_payload
            )

        response = {
            "virtual_account": va_response["virtual_account"],
            "valid_until": va_response["valid_until"],
            "amount": va_response["amount"],
        }
        return ok(response)
