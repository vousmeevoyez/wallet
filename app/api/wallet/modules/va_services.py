"""
    Virtual Account Services
    ________________
    This is module that serve everything related to Virtual Account
"""
#pylint: disable=bad-whitespace
#pylint: disable=no-self-use
from datetime import datetime, timedelta
import pytz

from sqlalchemy.exc import IntegrityError

from app.api import db

# models
from app.api.models import Wallet
from app.api.models import VirtualAccount
from app.api.models import VaType

# serializer
from app.api.serializer import WalletSchema
from app.api.serializer import TransactionSchema
from app.api.serializer import VirtualAccountSchema

from app.api.http_response import request_not_found

# configuration
from app.config import config

VIRTUAL_ACCOUNT_CONFIG = config.Config.VIRTUAL_ACCOUNT_CONFIG
TASK_CONFIG = config.Config.TASK_CONFIG

class VirtualAccountServices:
    """ Virtual Account Services Class"""

    TIMEZONE = pytz.timezone("Asia/Jakarta")

    def _get_datetime_expired(self, bank_id, va_type):
        """ function to set virtual account datetime_expired based on which
        bank and which type"""
        timeout = VIRTUAL_ACCOUNT_CONFIG[bank_id]

        if va_type == "CREDIT":
            datetime_expired = datetime.now(self.TIMEZONE) \
                             + timedelta(hours=timeout["CREDIT_VA_TIMEOUT"])
        elif va_type == "DEBIT":
            datetime_expired = datetime.now(self.TIMEZONE) \
                             + timedelta(minutes=timeout["DEBIT_VA_TIMEOUT"])
        return datetime_expired
    #end def

    def add(self, params, session=None):
        """
            create virtual account record on database here and return system
            generated transaction and virtual account id
            args :
                bank_code -- bank code
                params -- wallet_id, name, type
                session -- database session (optional)
        """
        wallet_id = int(params["wallet_id"])
        bank_id = params["bank_id"]
        name = params["name"]
        va_type = params["type"]
        # fetch va type here
        va_type = VaType.query.filter_by(key=va_type).first()

        # check is the user already have a VA or not
        search_va = VirtualAccount.query.filter_by(
            wallet_id=wallet_id,
            va_type_id=va_type.id,
            bank_id=bank_id
        ).first()
        if search_va is not None:
            raise AlreadyExistVAError
        #end if

        # set session if empty
        if session is None:
            session = db.session
        #end if
        session.begin(nested=True)

        datetime_expired = self._get_datetime_expired(bank_id, params["type"])

        # CREATE VIRTUAL ACCOUNT ON DATABASES FIRST
        virtual_account = VirtualAccount(
            name=name,
            wallet_id=wallet_id,
            status=TASK_CONFIG["PENDING"],# PENDING FIRST
            bank_id=bank_id,
            va_type_id=va_type.id,
            datetime_expired=datetime_expired
        )
        virtual_account_id = virtual_account.generate_va_number()
        transaction_id = virtual_account.generate_trx_id()

        try:
            session.add(virtual_account)
            session.commit()
        except IntegrityError as error:
            raise AlreadyExistVAError()
        #end try

        response = {
            "datetime_expired" : datetime_expired,
            "virtual_account_id" : virtual_account_id,
            "transaction_id" : transaction_id
        }
        return response
    #end def
#end class
