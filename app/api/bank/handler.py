"""
    Bank Handler
    ________________
    this is module that handle request and dipsatch it to various bank
"""
import pytz
from datetime import datetime, timedelta

from app.api        import db
from app.api.models import VirtualAccount, Wallet, Bank, VaType

from app.api.config import config

# import all bank here
from app.api.bank.bni.helper import BNI

VIRTUAL_ACCOUNT_CONFIG = config.Config.VIRTUAL_ACCOUNT_CONFIG

class Bank_:
    """ factory method for all bank"""
    @staticmethod
    def factory(bank_name):
        """ static method function to force all bank imported here"""
        if bank_name == "BNI":
            return BNI()
    #end def
#end class

class BankHandler:
    """ this is class that handle function to various bank module"""

    TIMEZONE = pytz.timezone("Asia/Jakarta")

    def __init__(self, bank_name):
        # set necessary information here
        self.bank_name = bank_name
        # assign bank object
        self.bank = Bank_.factory(bank_name)
        # convert bank name to bank id
        self.bank_id = self._bank_name_to_id(bank_name)
    #end def

    def _get_datetime_expired(self, va_type):
        """ function to set virtual account datetime_expired based on which
        bank and which type"""
        timeout = VIRTUAL_ACCOUNT_CONFIG[self.bank_name]

        if va_type == "CREDIT":
            datetime_expired = datetime.now(self.TIMEZONE) \
                             + timedelta(hours=timeout["CREDIT_VA_TIMEOUT"])
        elif va_type == "DEBIT":
            datetime_expired = datetime.now(self.TIMEZONE) \
                             + timedelta(minutes=timeout["DEBIT_VA_TIMEOUT"])
        return datetime_expired
    #end def

    @staticmethod
    def _bank_name_to_id(bank_name):
        # for now we only support BNI but more bank in future
        bank_code = ""
        if bank_name == "BNI":
            bank_code = "009"
        bank = Bank.query.filter_by(code=bank_code).first()
        return bank.id
    #end def

    def _create_va(self, params, session=None):
        """
            create virtual account record on database here and return system
            generated transaction and virtual account id
            args :
                bank_code -- bank code
                params -- wallet_id, name, type
                session -- database session (optional)
        """
        response = {
            "status" : "SUCCESS",
            "data"   : None
        }
        # fetch va type here
        va_type = VaType.query.filter_by(key=params["type"]).first()

        # check is the user already have a VA or not
        search_va = VirtualAccount.query.filter_by(
            wallet_id=int(params["wallet_id"]),
            va_type_id=va_type.id,
            bank_id=self.bank_id
        ).first()
        if search_va is not None:
            response["status"] = "FAILED"
            response["data"] = "VA_ALREADY_EXISTED"
            return response
        #end if

        # set session if empty
        if session is None:
            session = db.session
        #end if
        session.begin(subtransactions=True)

        datetime_expired = self._get_datetime_expired(params["type"])

        # CREATE VIRTUAL ACCOUNT ON DATABASES FIRST
        virtual_account = VirtualAccount(
            name=params["name"],
            wallet_id=int(params["wallet_id"]),
            status=True,# active
            bank_id=self.bank_id,
            va_type_id=va_type.id,
            datetime_expired=datetime_expired
        )
        virtual_account_id = virtual_account.generate_va_number()
        transaction_id = virtual_account.generate_trx_id()

        session.add(virtual_account)

        response["data"] = {
            "datetime_expired" : datetime_expired,
            "virtual_account_id" : virtual_account_id,
            "transaction_id" : transaction_id
        }
        return response
    ##end

    def dispatch(self, operation, params):
        """
            method to dispatch the request to specific bank object
            args:
                bank_name -- Bank Name
                operation -- Operation
                params -- params
        """
        if operation == "CREATE_VA":
            # create va record first
            va_creation_resp = self._create_va(params)

            # add more information to params
            params["datetime_expired"] = va_creation_resp["data"]["datetime_expired"]
            params["virtual_account_id"] = va_creation_resp["data"]["virtual_account_id"]
            params["transaction_id"] = va_creation_resp["data"]["transaction_id"]

            if params["type"] == "DEBIT" and self.bank_name == "BNI":
                result = self.bank.call("CREATE_VA_CARDLESS", params)
            #end if
            result = self.bank.call("CREATE_VA", params)
        elif operation == "TRANSFER":
            result = self.bank.call("TRANSFER", params)
        elif operation == "CHECK_BALANCE":
            result = self.bank.call("CHECK_BALANCE", params)
        #end if
        return result
    #end def
#end class
