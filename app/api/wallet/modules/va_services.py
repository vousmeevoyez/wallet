"""
    Virtual Account Services
    ________________
    This is module that serve everything related to Virtual Account
"""
#pylint: disable=bad-whitespace
#pylint: disable=no-self-use
from sqlalchemy.exc import IntegrityError

from app.api import db
# models
from app.api.models import Bank
from app.api.models import Wallet
from app.api.models import VirtualAccount
from app.api.models import VaType

# serializer
from app.api.serializer import WalletSchema
from app.api.serializer import TransactionSchema
from app.api.serializer import VirtualAccountSchema

# configuration
from app.config import config

from app.api.http_response import created

from app.api.exception.virtual_account import *

VIRTUAL_ACCOUNT_CONFIG = config.Config.VIRTUAL_ACCOUNT_CONFIG
STATUS_CONFIG = config.Config.STATUS_CONFIG

class VirtualAccountServices:
    """ Virtual Account Services Class"""
    def __init__(self, va_id):
        va_record = VirtualAccount.query.filter_by(id=va_id).first()
        if va_record is None:
            raise VaNotFoundError

    @staticmethod
    def add(virtual_account, params):
        """
            create virtual account record on database here and return system
            generated transaction and virtual account id
            args :
                bank_code -- bank code
                params -- wallet_id, name, type
                session -- database session (optional)
        """
        bank_name = params["bank_name"]
        va_type = params["type"]
        wallet_id =params["wallet_id"]

        # fetch va type id
        va_type = VaType.query.filter_by(key=va_type).first()

        # fetch bank id
        keyword = "%{}%".format(bank_name)
        bank = Bank.query.filter(Bank.name.like(keyword)).first()

        # put va creation in the queue
        virtual_account.status = STATUS_CONFIG["PENDING"]
        virtual_account.wallet_id = wallet_id
        virtual_account.va_type_id = va_type.id
        virtual_account.bank_id = bank.id

        virtual_account_id = virtual_account.generate_va_number()
        transaction_id = virtual_account.generate_trx_id()
        datetime_expired = virtual_account.get_datetime_expired(bank_name, params["type"])

        try:
            db.session.add(virtual_account)
            db.session.commit()
        except IntegrityError as error:
            db.session.rollback()
            raise AlreadyExistVAError
        #end try

        response = {
            "virtual_account_id" : virtual_account_id,
        }
        return created(response)
    #end def
#end class
