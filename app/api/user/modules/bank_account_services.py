"""
    User Bank Account Services
    ___________________________
    this is module that handle bank account process for user
"""
#pylint: disable=no-self-use
from sqlalchemy.exc import IntegrityError, InvalidRequestError

from app.api import db
# models
from app.api.models import User
from app.api.models import Bank
from app.api.models import BankAccount
# serializer
from app.api.serializer import BankAccountSchema
# http response
from app.api.http_response import created
from app.api.http_response import no_content

from app.api.exception.user import UserNotFoundError
from app.api.exception.bank import BankNotFoundError
from app.api.exception.bank import BankAccountNotFoundError
from app.api.exception.bank import DuplicateBankAccountError

# configuration
from app.config import config

class BankAccountServices:
    """ Bank Account Services Class"""
    def __init__(self, user_id, bank_code=None, bank_account_id=None):
        user_record = User.query.filter_by(id=user_id).first()
        if user_record is None:
            raise UserNotFoundError
        #end if

        # get bank id from bank code
        bank_record = None
        if bank_code is not None:
            bank_record = Bank.query.filter_by(code=bank_code).first()

            if bank_record is None:
                raise BankNotFoundError
            #end if
        #end if

        bank_account_record = None
        if bank_account_id is not None:
            bank_account_record = BankAccount.query.filter_by(user_id=user_id,
                                                              id=bank_account_id).first()
            if bank_account_record is None:
                raise BankAccountNotFoundError
        #end if

        self.user = user_record
        self.bank = bank_record
        self.bank_account = bank_account_record

    def add(self, bank_account):
        """ add bank account"""
        bank_account.bank_id = self.bank.id
        bank_account.user_id = self.user.id

        try:
            db.session.add(bank_account)
            db.session.commit()
        except IntegrityError as error:
            db.session.rollback()
            raise DuplicateBankAccountError
        #end try
        response = {
            "bank_account_id" : bank_account.id
        }
        return created(response)
    #end def

    def show(self):
        """ method to show user bank accounts"""
        bank_accounts = BankAccount.query.filter_by(user_id=self.user.id).all()
        response = BankAccountSchema(many=True).dump(bank_accounts).data
        return response
    #end def

    def update(self, params):
        """ update user bank account information"""
        self.bank_account.label = params["label"]
        self.bank_account.name = params["name"]
        self.bank_account.account_no = params["account_no"]
        self.bank_account.bank_code = self.bank.code

        db.session.commit()
        return no_content()
    #end def

    def remove(self):
        """ remove bank account"""
        db.session.delete(self.bank_account)
        db.session.commit()
        return no_content()
    #end def
#end class
