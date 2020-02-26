"""
    Transfer Services
    _________________
    this is module that serve request from wallet transfer :w
    routes
"""
# pylint: disable=no-self-use
# pylint: disable=import-error
# pylint: disable=bad-whitespace
# pylint: disable=invalid-name
from sqlalchemy.exc import IntegrityError
# core
from app.api import scheduler, db
# models
from app.api.models import BankAccount, User
# serializer
from app.api.serializer import UserSchema
# core
from app.api.wallets.modules.wallet_core import WalletCore
from app.api.quotas.modules.quota_services import QuotaServices
# transactions
from app.api.transactions.factories.helper import process_transaction
# error response
from app.api.const import WALLET
from app.api.const import ERROR as error_response
# exceptions
from app.lib.http_error import (
    UnprocessableEntity,
    RequestNotFound
)
# http response
from app.lib.http_response import accepted, ok
# utility
from app.api.utility.utils import validate_uuid


class TransferServices(WalletCore):
    """ Transfer Services"""

    @staticmethod
    def calculate_transfer_fee(destination, method=None):
        """ calculate transfer fee based on method and destination"""
        transfer_fee = 0

        bank_account = BankAccount.query.filter_by(
            id=validate_uuid(destination)
        ).first()
        if bank_account:
            if bank_account.bank.code != "009":
                transfer_fee = WALLET["TRANSFER_FEE"][method]
        return transfer_fee

    def internal_transfer(self, params):
        """ method to transfer money internally"""
        amount = params["amount"]
        notes = params["notes"]
        flag = params["types"] or "TRANSFER"

        if float(amount) > float(self.source.balance):
            raise UnprocessableEntity(
                error_response["INSUFFICIENT_BALANCE"]["TITLE"],
                error_response["INSUFFICIENT_BALANCE"]["MESSAGE"],
            )
        # end if

        debit_trx = process_transaction(
            source=self.source,
            destination=self.destination,
            amount=-amount,
            flag=flag,
            notes=notes,
        )

        destination_flag = "RECEIVE_" + flag

        credit_trx = process_transaction(
            source=self.source,
            destination=self.destination,
            amount=amount,
            flag=destination_flag,
            notes=notes,
        )

        # link debit and credit
        credit_trx.parent_id = debit_trx.id
        db.session.commit()

        return accepted({"id": str(debit_trx.id)})

    # end def

    def external_transfer(self, params, flag="BANK_TRANSFER"):
        """ method to transfer money externally"""
        bank_account_id = params["destination"]
        amount = params["amount"]
        notes = params["notes"]

        # calculate transfer fee here
        # for now only online
        transfer_fee = self.calculate_transfer_fee(bank_account_id, "CLEARING")

        if float(amount) + float(transfer_fee) > float(self.source.balance):
            raise UnprocessableEntity(
                error_response["INSUFFICIENT_BALANCE"]["TITLE"],
                error_response["INSUFFICIENT_BALANCE"]["MESSAGE"],
            )
        # end if

        # fetch bank information from bank account id here
        bank_account = BankAccount.query.filter_by(
            id=validate_uuid(bank_account_id)
        ).first()
        if bank_account is None:
            raise RequestNotFound(
                error_response["BANK_ACC_NOT_FOUND"]["TITLE"],
                error_response["BANK_ACC_NOT_FOUND"]["MESSAGE"],
            )
        # end if

        bank_transfer_trx = process_transaction(
            source=self.source,
            destination=bank_account.account_no,
            amount=-amount,
            flag=flag,
            notes=notes,
        )

        # create fee payment if transfer fee > 0
        if transfer_fee > 0:
            fee_trx = process_transaction(
                source=self.source,
                destination="N/A",
                amount=-transfer_fee,
                flag="TRANSFER_FEE",
                notes=notes,
            )

            # map bank transfer trx -> fee trx
            fee_trx.parent_id = bank_transfer_trx.id

            # check whether this transaction and user valid for reward
            reward_info = QuotaServices(
                wallet_id=str(self.source.id),
                transaction_id=bank_transfer_trx.id
            ).use_quota()
            if reward_info["is_rewarded"]:
                reward_trx = process_transaction(
                    source="N/A",
                    destination=self.source,
                    amount=reward_info["reward_amount"],
                    flag="CASHBACK",
                )
                # map fee trx -> reward trx
                # so it became
                # bank trx -> fee trx -> reward trx
                reward_trx.parent_id = fee_trx.id

            # commit everything
            db.session.commit()
        # end if
        return accepted({"id": str(bank_transfer_trx.id)})

    # end def

    def checkout(self, phone_ext, phone_number, fields=None):
        """
            Checkout Transfer
            exchange phone number and return wallet available for that users
        """
        user = User.query.filter_by(
            phone_ext=phone_ext, phone_number=phone_number
        ).first()
        if user is None:
            raise RequestNotFound(
                error_response["USER_NOT_FOUND"]["TITLE"],
                error_response["USER_NOT_FOUND"]["MESSAGE"],
            )
        # end if

        # serialize
        user_info = UserSchema().dump(user).data
        if fields is not None:
            user_info = UserSchema(only=fields).dump(user).data
        return ok(user_info)
