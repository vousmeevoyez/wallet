"""
    User Bank Account Services
    ___________________________
    this is module that handle bank account process for user
"""
#pylint: disable=no-self-use
from flask          import request, jsonify
from sqlalchemy     import exists
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from marshmallow    import ValidationError

from app.api            import db
# models
from app.api.models     import User
from app.api.models     import Bank
from app.api.models     import BankAccount
# serializer
from app.api.serializer import BankAccountSchema
# http response
from app.api.http_response import bad_request
from app.api.http_response import unprocessable_entity
from app.api.http_response import request_not_found
from app.api.http_response import created
from app.api.http_response import no_content
# configuration
from app.config import config

ERROR = config.Config.ERROR_HEADER

class BankAccountServices:
    """ Bank Account Services Class"""

    def add(self, params):
        """ add bank account"""

        user_id = params["user_id"]
        bank_code = params["bank_code"]

        # check user id first
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return request_not_found(ERROR["USER_NOT_FOUND"])
        #end if

        # get bank id from bank code
        bank = Bank.query.filter_by(code=bank_code).first()
        if bank is None:
            return request_not_found(ERROR["BANK_NOT_FOUND"])
        #end if

        # create bank_account
        bank_account = BankAccount(
            label=params["label"],
            name=params["name"],
            account_no=params["account_no"],
            bank_id=bank.id,
            user_id=user_id,
        )

        try:
            db.session.add(bank_account)
            db.session.commit()
        except IntegrityError as err:
            db.session.rollback()
            return unprocessable_entity(ERROR["DUPLICATE_BANK_ACC"])
        #end try
        return created()
    #end def

    def show(self, params):
        """ method to show user bank accounts"""
        user_id = params["user_id"]

        # check user id first
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return request_not_found(ERROR["USER_NOT_FOUND"])
        #end if

        bank_accounts = BankAccount.query.filter_by(user_id=user.id).all()

        response = BankAccountSchema(many=True).dump(bank_accounts).data
        return response
    #end def

    def update(self, params):
        """ update user bank account information"""

        user_bank_account_id = params["user_bank_account_id"]
        user_id = params["user_id"]

        bank_account = BankAccount.query.filter_by(user_id=user_id, id=user_bank_account_id).first()
        if bank_account is None:
            return request_not_found(ERROR["BANK_ACC_NOT_FOUND"])
        #end if

        # get bank id from bank code
        bank = Bank.query.filter_by(code=params["bank_code"]).first()
        if bank is None:
            return request_not_found(ERROR["BANK_NOT_FOUND"])
        #end if

        bank_account.label = params["label"]
        bank_account.name = params["name"]
        bank_account.account_no = params["account_no"]
        bank_account.bank_code = bank.id

        db.session.commit()
        return no_content()
    #end def

    def remove(self, params):
        """ remove bank account"""

        user_bank_account_id = params["user_bank_account_id"]
        user_id = params["user_id"]

        bank_account = BankAccount.query.filter_by(user_id=user_id, id=user_bank_account_id).first()
        if bank_account is None:
            return request_not_found(ERROR["BANK_ACC_NOT_FOUND"])
        #end if

        db.session.delete(bank_account)
        db.session.commit()

        return no_content()
    #end def
#end class
