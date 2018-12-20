import traceback
from datetime import datetime, timedelta

from flask          import request, jsonify
from sqlalchemy     import exists
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from marshmallow    import ValidationError

from app.api            import db
from app.api.wallet     import helper
from app.api.models     import User, Bank, BankAccount
from app.api.serializer import BankAccountSchema
from app.api.errors     import bad_request, internal_error, request_not_found
from app.api.config     import config

RESPONSE_MSG = config.Config.RESPONSE_MSG

class UserBankAccountController:

    def __init__(self):
        pass
    #end def

    def add(self, params):
        response = {}

        try:
            user_id   = params["user_id"]
            bank_code = params["bank_code"]

            # check user id first
            user = User.query.filter_by(id=user_id).first()
            if user == None:
                return request_not_found(RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])
            #end if

            # get bank id from bank code
            bank = Bank.query.filter_by(code=bank_code).first()
            if bank == None:
                return request_not_found(RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])
            #end if

            # create bank_account
            bank_account = BankAccount(
                label=params["label"],
                name=params["name"],
                account_no=params["account_no"],
                bank_id=bank.id,
                user_id=user_id,
            )

            db.session.add(bank_account)
            db.session.commit()

        except IntegrityError as err:
            print(err)
            session.rollback()
            return internal_error(RESPONSE_MSG["FAILED"]["ERROR_ADDING_RECORD"])
        #end try

        response["message"] = RESPONSE_MSG["SUCCESS"]["CREATE_BANK_ACCOUNT"]
        return response
    #end def

    def show(self, params):
        response = {}

        user_id   = params["user_id"]

        # check user id first
        user = User.query.filter_by(id=user_id).first()
        if user == None:
            return request_not_found(RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])
        #end if

        bank_accounts = BankAccount.query.filter_by(user_id=user.id).all()

        response["data"] = BankAccountSchema(many=True).dump(bank_accounts).data
        return response
    #end def

    def update(self, params):
        response = {}

        user_bank_account_id = params["user_bank_account_id"]
        user_id              = params["user_id"]

        bank_account = BankAccount.query.filter_by(user_id=user_id, id=user_bank_account_id).first()
        if bank_account == None:
            return request_not_found(RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])
        #end if

        # get bank id from bank code
        bank = Bank.query.filter_by(code=params["bank_code"]).first()
        if bank == None:
            return request_not_found(RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])
        #end if

        bank_account.label      = params["label"]
        bank_account.name       = params["name" ]
        bank_account.account_no = params["account_no"]
        bank_account.bank_code  = bank.id

        db.session.commit()

        response["message"] = RESPONSE_MSG["SUCCESS"]["UPDATE_BANK_ACCOUNT"]
        return response
    #end def

    def remove(self, params):
        response = {}

        user_bank_account_id = params["user_bank_account_id"]
        user_id              = params["user_id"]

        bank_account = BankAccount.query.filter_by(user_id=user_id, id=user_bank_account_id).first()
        if bank_account == None:
            return request_not_found(RESPONSE_MSG["FAILED"]["RECORD_NOT_FOUND"])
        #end if

        db.session.delete(bank_account)
        db.session.commit()

        response["message"] = RESPONSE_MSG["SUCCESS"]["REMOVE_BANK_ACCOUNT"]
        return response
    #end def
#end class
