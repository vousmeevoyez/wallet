"""
    User Bank Account Services
    ___________________________
"""
# pylint: disable=no-self-use
# pylint: disable=no-name-in-module
# pylint: disable=import-error
from sqlalchemy.exc import IntegrityError, InvalidRequestError

# database
from app.api import db

# models
from app.api.models import User
from app.api.models import Bank
from app.api.models import BankAccount

# serializer
from app.api.serializer import BankAccountSchema

# http response
from app.lib.http_response import created, no_content
from app.api.utility.utils import validate_uuid

# exception
from app.lib.http_error import RequestNotFound, UnprocessableEntity

# error
from app.api.const import ERROR as error_response


class BankAccountServices:
    """ Bank Account Services Class"""

    def __init__(self, user_id, bank_id=None, bank_account_id=None):
        user_record = User.query.filter_by(id=validate_uuid(user_id)).first()
        if user_record is None:
            raise RequestNotFound(
                error_response["USER_NOT_FOUND"]["TITLE"],
                error_response["USER_NOT_FOUND"]["MESSAGE"],
            )
        # end if

        # get bank id from bank code
        bank_record = None
        if bank_id is not None:
            bank_record = Bank.query.filter_by(id=validate_uuid(bank_id)).first()

            if bank_record is None:
                raise RequestNotFound(
                    error_response["BANK_NOT_FOUND"]["TITLE"],
                    error_response["BANK_NOT_FOUND"]["MESSAGE"],
                )
            # end if
        # end if

        bank_account_record = None
        if bank_account_id is not None:
            bank_account_record = BankAccount.query.filter_by(
                user_id=validate_uuid(user_id), id=validate_uuid(bank_account_id)
            ).first()
            if bank_account_record is None:
                raise RequestNotFound(
                    error_response["BANK_ACC_NOT_FOUND"]["TITLE"],
                    error_response["BANK_ACC_NOT_FOUND"]["MESSAGE"],
                )
        # end if

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
            raise UnprocessableEntity(
                error_response["DUPLICATE_BANK_ACCOUNT"]["TITLE"],
                error_response["DUPLICATE_BANK_ACCOUNT"]["MESSAGE"],
            )
        # end try
        response = {"bank_account_id": str(bank_account.id)}
        return created(response)

    # end def

    def show(self):
        """ method to show user bank accounts"""
        bank_accounts = BankAccount.query.filter_by(user_id=self.user.id).all()
        response = BankAccountSchema(many=True).dump(bank_accounts).data
        return response

    # end def

    def info(self):
        """ method to show user bank accounts"""
        response = BankAccountSchema().dump(self.bank_account)
        return response

    # end def

    def update(self, params):
        """ update user bank account information"""
        self.bank_account.label = params["label"]
        self.bank_account.name = params["name"]
        self.bank_account.account_no = params["account_no"]
        self.bank_account.bank_code = self.bank.code

        db.session.commit()
        return no_content()

    # end def

    def remove(self):
        """ remove bank account"""
        db.session.delete(self.bank_account)
        db.session.commit()
        return no_content()

    # end def


# end class
