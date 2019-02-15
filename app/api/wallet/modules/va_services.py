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
from app.api.models import *
# serializer
from app.api.serializer import *
# configuration
from app.config import config
# http response
from app.api.http_response import *
from app.api.error.http import *

from task.bank.tasks import BankTask

VIRTUAL_ACCOUNT_CONFIG = config.Config.VIRTUAL_ACCOUNT_CONFIG
STATUS_CONFIG = config.Config.STATUS_CONFIG
ERROR_CONFIG = config.Config.ERROR_CONFIG

class VirtualAccountServices:
    """ Virtual Account Services Class"""
    def __init__(self, virtual_account_no):
        va_record = \
        VirtualAccount.query.filter(VirtualAccount.account_no == virtual_account_no,
                                    VirtualAccount.status != STATUS_CONFIG["DEACTIVE"]).first()
        if va_record is None:
            raise RequestNotFound(ERROR_CONFIG["VA_NOT_FOUND"]["TITLE"],
                                  ERROR_CONFIG["VA_NOT_FOUND"]["MESSAGE"])

        self.virtual_account = va_record

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
        wallet_id = params["wallet_id"]
        amount = params["amount"]

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
        virtual_account.amount = amount

        virtual_account_number = virtual_account.generate_va_number()
        transaction_id = virtual_account.generate_trx_id()
        datetime_expired = virtual_account.get_datetime_expired(bank_name, params["type"])

        try:
            db.session.add(virtual_account)
            db.session.commit()
        except IntegrityError as error:
            db.session.rollback()
            raise UnprocessableEntity(ERROR_CONFIG["DUPLICATE_VA"]["TITLE"],
                                      ERROR_CONFIG["DUPLICATE_VA"]["MESSAGE"])
        #end try

        # create va in the background here
        task_result = BankTask().create_va.delay(virtual_account.id)

        response = {
            "virtual_account" : virtual_account_number,
            "valid_until"     : datetime_expired,
            "amount"          : amount
        }
        return created(response)
    #end def

    def info(self):
        """
            return Virtual Account information details
        """
        virtual_account = \
        VirtualAccountSchema().dump(self.virtual_account).data
        response = {
            "data" : virtual_account
        }
        return response
    #end def

    def remove(self):
        """
            return Virtual Account information details
        """
        self.virtual_account.status = STATUS_CONFIG["DEACTIVE"]
        db.session.commit()
        return no_content()
    #end def

    def update(self, params):
        """
            update Virtual Account information stored on the system
        """
        # update existing va with new generated value
        virtual_account_number = self.virtual_account.generate_va_number()
        transaction_id = self.virtual_account.generate_trx_id()
        datetime_expired = \
        self.virtual_account.get_datetime_expired(params["bank_name"], params["type"])
        self.virtual_account.trx_amount = params["amount"]
        
        response = {
            "virtual_account" : virtual_account_number,
            "valid_until"     : datetime_expired,
            "amount"          : params["amount"]
        }
        return response
    #end def
#end class
