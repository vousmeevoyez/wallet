"""
    Withdraw Services Class
    _______________________
    Handle withdraw request process
"""
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError

from app.api            import db
from app.api.models     import Wallet, Withdraw
# http response
from app.api.exception.wallet import *

from app.config     import config

TRANSACTION_NOTES = config.Config.TRANSACTION_NOTES
WALLET_CONFIG = config.Config.WALLET_CONFIG
VIRTUAL_ACCOUNT_CONFIG = config.Config.VIRTUAL_ACCOUNT_CONFIG
STATUS_CONFIG = config.Config.STATUS_CONFIG

class WithdrawServices:
    """ class that handle request to withdraw """
    def __init__(self, wallet_id, pin):
        wallet_record = Wallet.query.filter_by(id=wallet_id,
                                               status=STATUS_CONFIG["ACTIVE"]).first()
        if wallet_record is None:
            raise WalletNotFoundError(wallet_id)
        #end if

        if wallet_record.check_pin(pin) is not True:
            raise IncorrectPinError
        #end if

        self.wallet = wallet_record

    def request(self, params):
        """ handle withdraw request """
        amount = float(params["amount"])

        if amount < float(WALLET_CONFIG["MINIMAL_WITHDRAW"]):
            raise MinimalWithdrawError
        #end if

        if amount > float(WALLET_CONFIG["MAX_WITHDRAW"]):
            raise MaxWithdrawError
        #end if

        if amount > float(self.wallet.balance):
            raise InsufficientBalanceError(self.wallet.balance, amount)
        #end if

        # before creating a cardless va, we need to make sure there's no ongoing withdraw request
        pending_withdraw = Withdraw.query.filter(Withdraw.wallet_id == self.wallet.id,
                                                 Withdraw.valid_until > datetime.now()).count()
        if pending_withdraw > 0:
            raise RaisePendingWithdrawError(self.wallet.id, amount)
        #end if

        # creating withdraw record and set it to valid for certain period of time
        valid_until = datetime.now() + \
        timedelta(hours=VIRTUAL_ACCOUNT_CONFIG["BNI"]["DEBIT_VA_TIMEOUT"])
        withdraw = Withdraw(
            wallet_id=self.wallet.id,
            valid_until=valid_until,
        )
        db.session.add(withdraw)

        user_info = self.wallet.user
        # generate msisdn
        msisdn = user_info.phone_ext + user_info.phone_number

        va_payload = {
            "wallet_id"        : self.wallet.id,
            "amount"           : int(amount),
            "customer_name"    : user_info.name,
            "customer_phone"   : msisdn,
        }

        """
        va_response = bank_helper.EcollectionHelper().create_va("CARDLESS", va_payload, session)
        if va_response["status"] != "SUCCESS":
            session.rollback()
            return bad_request(va_response["data"])
        #end if
        """

        db.session.commit()

        response = {
            "valid_until" : str(valid_until.timestamp())
        }
        return response
    #end def
#end class
