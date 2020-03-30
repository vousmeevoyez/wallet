"""
    Virtual Account Services
    ________________
"""
# pylint: disable=bad-whitespace
# pylint: disable=no-self-use
# pylint: disable=no-name-in-module
# pylint: disable=import-error
# pylint: disable=no-member
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

# database
from app.api import db

# models
from app.api.models import VirtualAccount, Bank, VaType, VaLog

# serializer
from app.api.serializer import VirtualAccountSchema, VaLogSchema
from app.lib.http_response import ok, created, no_content
from app.lib.http_error import RequestNotFound, UnprocessableEntity

# const
from app.api.const import STATUS

# error response
from app.api.const import ERROR as error_response

from app.api.banks.modules.bank_services import BankServices

# bank task
from task.bank.tasks import BankTask


class VirtualAccountServices:
    """ Virtual Account Services Class"""

    def __init__(self, virtual_account_no=None):
        if virtual_account_no is not None:
            va_record = VirtualAccount.query.filter(
                VirtualAccount.account_no == virtual_account_no,
                VirtualAccount.status != STATUS["DEACTIVE"],
            ).first()
            if va_record is None:
                raise RequestNotFound(
                    error_response["VA_NOT_FOUND"]["TITLE"],
                    error_response["VA_NOT_FOUND"]["MESSAGE"],
                )

            self.virtual_account = va_record

    @staticmethod
    def add(name, wallet_id, bank_code, va_type, amount):
        """
            create virtual account record on database here and return system
            generated transaction and virtual account id
            args :
                bank_code -- bank code
                params -- wallet_id, name, type
                session -- database session (optional)
        """
        virtual_account = VirtualAccount(name=name)

        # fetch va type id
        va_type_obj = VaType.query.filter_by(key=va_type).first()
        # fetch bank id
        bank = Bank.query.filter_by(code=bank_code).first()

        # put va creation in the queue
        virtual_account.wallet_id = wallet_id
        virtual_account.va_type_id = va_type_obj.id
        virtual_account.bank_id = bank.id
        virtual_account.amount = amount

        virtual_account.generate_trx_id()
        virtual_account_number = virtual_account.generate_va_number()
        datetime_expired = virtual_account.get_datetime_expired(bank_code, va_type)

        try:
            db.session.add(virtual_account)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise UnprocessableEntity(
                error_response["DUPLICATE_VA"]["TITLE"],
                error_response["DUPLICATE_VA"]["MESSAGE"],
            )
        # end try

        # create va in the background here
        BankTask().create_va.apply_async(args=[virtual_account.id], queue="bank")

        response = {
            "virtual_account": virtual_account_number,
            "valid_until": datetime_expired,
            "amount": amount,
        }
        return created(response)

    # end def

    def show(self):
        """
            return all Virtual Account
        """
        virtual_accounts = VirtualAccount.query.all()
        response = VirtualAccountSchema(many=True).dump(virtual_accounts).data
        return ok(response)

    # end def

    def info(self):
        """
            return Virtual Account information details
        """
        virtual_account = VirtualAccountSchema().dump(self.virtual_account).data
        return {"data": virtual_account}

    # end def

    def get_logs(self):
        """
            return all Virtual Account logs that recorded
        """
        logs = (
            VaLog.query.join(VirtualAccount)
            .filter(VaLog.virtual_account_id == self.virtual_account.id)
            .all()
        )
        response = VaLogSchema(many=True).dump(logs).data
        return ok(response)

    # end def

    def update(self, name, datetime_expired=None):
        """
            update Virtual Account information details
        """
        self.virtual_account.name = name
        if datetime_expired is not None:
            self.virtual_account.datetime_expired = datetime.fromisoformat(
                datetime_expired
            )

        db.session.commit()

        BankTask().update_va.apply_async(args=[self.virtual_account.id], queue="bank")
        return no_content()

    # end def

    def remove(self):
        """
            return Virtual Account information details
        """
        self.virtual_account.status = STATUS["DEACTIVE"]
        db.session.commit()
        return no_content()

    # end def

    def reactivate(self, bank_code, va_type, amount):
        """
            Re create VA that already exist with same information
        """
        # update existing va with new generated value
        self.virtual_account.generate_trx_id()
        datetime_expired = self.virtual_account.get_datetime_expired(bank_code, va_type)
        self.virtual_account.amount = amount

        # commit everything
        db.session.commit()

        BankTask().create_va.apply_async(args=[self.virtual_account.id], queue="bank")

        response = {
            "virtual_account": str(self.virtual_account.account_no),
            "valid_until": datetime_expired,
            "amount": amount,
        }
        return response

    # end def


# end class


def bulk_update_va():
    """
        we go check all virtual accounts and if almost expire we extend it
        otherwise we just recreate it
    """
    va_type = VaType.query.filter_by(key="CREDIT").first()
    virtual_accounts = VirtualAccount.query.filter_by(
        va_type_id=va_type.id, status=STATUS["ACTIVE"]
    ).all()
    for virtual_account in virtual_accounts:
        try:
            va_info = BankServices().get_account_information(virtual_account.account_no)
        except UnprocessableEntity as error:
            print(error)
            print("Failed to fetch {}".format(virtual_account.account_no))
        else:
            # if va info status == 2 it means expired we need to recreate it
            # if va status == 1 we just extend it
            current_va_status = va_info["bank_account_info"]["status"]
            if current_va_status == "1":
                # set to 10 years from now
                expired_at = datetime.utcnow() + timedelta(days=365 * 10)
                expired_at = expired_at.isoformat()
                VirtualAccountServices(virtual_account.account_no).update(
                    virtual_account.name, expired_at
                )
            elif current_va_status == "2":
                VirtualAccountServices(virtual_account.account_no).reactivate(
                    amount=0, bank_code="009", va_type="CREDIT"
                )


# end def
