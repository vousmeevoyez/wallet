"""
    Transfer Services
    _________________
    this is module that serve request from wallet transfer :w
    routes
"""
#pylint: disable=no-self-use
#pylint: disable=import-error
#pylint: disable=bad-whitespace
#pylint: disable=invalid-name
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from flask import current_app
# core
from app.api import scheduler
from app.api import db
# models
from app.api.models import *
# core
from app.api.wallets.modules.wallet_core import WalletCore
from app.api.wallets.modules.transaction_core import TransactionCore
# exceptions
from app.api.error.http import *
#http response
from app.api.http_response import *
# serializer
from app.api.serializer import UserSchema
# utility
from app.api.utility.utils import validate_uuid
# task
from task.bank.tasks import BankTask

class TransferServices(WalletCore):
    """ Transfer Services"""

    def calculate_transfer_fee(self, destination, method=None):
        """ calculate transfer fee based on method and destination"""
        transfer_fee = 0

        bank_account = BankAccount.query.filter_by(
            id=validate_uuid(destination)
        ).first()
        if bank_account:
            if bank_account.bank.code != "009":
                transfer_fee = self.wallet_config["TRANSFER_FEE"][method]
            # end if
        # end if
        return transfer_fee

    def auto_pay(self, wallet, payroll_amount):
        """ special function to deduct payroll automatically """
        # prevent circular import!
        from task.payment.tasks import PaymentTask

        response = {}

        plan = PaymentPlan.check_payment(wallet)
        if plan is not None:
            # make sure today is the due date to able deduct it
            due_date = plan.due_date
            payroll_date = datetime.utcnow()
            differences = payroll_date - due_date

            total_amount, plans = PaymentPlan.total(plan)

            # if there's no day differences and payroll is bigger than payment
            if differences.days == 0 and payroll_amount >= total_amount:
                # bank account
                current_app.logger.info("should trigger AUTO_PAY")
                PaymentTask.background_transfer.apply_async(args=[plan.id,
                                                                  "AUTO_PAY"],
                                                            queue="payment")
                response["data"] = {"message" : "AUTO_PAY"}
            else:
                current_app.logger.info("payroll_date : {}".format(payroll_date))
                current_app.logger.info("due_date : {}".format(due_date))
                current_app.logger.info("differences : {}".format(differences.days))
                current_app.logger.info("should trigger AUTO_DEBIT")
                # should switch to AUTO_DEBIT
                # if its early payroll should trigger auto debit on due date
                if differences.days < 0:
                    due_date = plan.due_date
                # if its payroll == due date but insufficient payroll, should
                # trigger auto debit on the next minutese
                elif differences.days == 0:
                    due_date = payroll_date + timedelta(minutes=1)
                elif differences.days > 0:
                    due_date = None
                # end if

                if due_date is not None:
                    job = scheduler.add_job(
                        lambda:
                        PaymentTask.background_transfer.apply_async(
                            args=[plan.id], queue="payment"
                        ),
                        trigger='date',
                        next_run_time=due_date
                    )
                    response["data"] = {"message" : "AUTO_DEBIT"}
                # end if
            # end if
        # end if
        return response
    # end def

    def internal_transfer(self, params):
        """ method to transfer money internally"""
        amount = params["amount"]
        transfer_notes = params["notes"]
        transfer_types = params["types"] or "TRANSFER_IN"

        if float(amount) > float(self.source.balance):
            raise UnprocessableEntity(self.error_response["INSUFFICIENT_BALANCE"]["TITLE"],
                                      self.error_response["INSUFFICIENT_BALANCE"]["MESSAGE"])
        #end if

        debit_trx = TransactionCore().process_transaction(
            source=self.source,
            destination=self.destination,
            amount=-amount,
            payment_type=False,
            transfer_types=transfer_types,
            transfer_notes=transfer_notes
        )

        destination_transfer_types = "RECEIVE_TRANSFER"
        if transfer_types == "PAYROLL":
            destination_transfer_types = "RECEIVE_PAYROLL"
            # should auto pay here
            result = self.auto_pay(self.destination, amount)
        # end if

        credit_trx = TransactionCore().process_transaction(
            source=self.source,
            destination=self.destination,
            amount=amount,
            payment_type=True,
            transfer_types=destination_transfer_types,
            transfer_notes=transfer_notes
        )

        # link debit and credit
        debit_trx.transaction_link_id = credit_trx.id
        credit_trx.transaction_link_id = debit_trx.id
        db.session.commit()

        return accepted({"id" : str(debit_trx.id)})
    #end def

    def external_transfer(self, params, flag="TRANSFER_OUT"):
        """ method to transfer money externally"""
        bank_account_id = params["destination"]
        amount = params["amount"]
        transfer_notes = params["notes"]

        # calculate transfer fee here
        # for now only online
        transfer_fee = self.calculate_transfer_fee(bank_account_id, "ONLINE")

        if float(amount) + float(transfer_fee) > float(self.source.balance):
            raise UnprocessableEntity(self.error_response["INSUFFICIENT_BALANCE"]["TITLE"],
                                      self.error_response["INSUFFICIENT_BALANCE"]["MESSAGE"])
        #end if

        # fetch bank information from bank account id here
        bank_account = BankAccount.query.filter_by(
            id=validate_uuid(bank_account_id)
        ).first()
        if bank_account is None:
            raise RequestNotFound(self.error_response["BANK_ACC_NOT_FOUND"]["TITLE"],
                                  self.error_response["BANK_ACC_NOT_FOUND"]["MESSAGE"])
        #end if

        bank_transfer_trx = TransactionCore().process_transaction(
            source=self.source,
            destination=bank_account.account_no,
            amount=-amount,
            payment_type=False,
            transfer_types=flag,
            transfer_notes=transfer_notes
        )

        # create fee payment if transfer fee > 0
        if transfer_fee > 0:
            fee_trx = TransactionCore().process_transaction(
                source=self.source,
                destination="N/A",
                amount=-transfer_fee,
                payment_type=False,
                transfer_types="TRANSFER_FEE",
                transfer_notes=transfer_notes
            )
            # link bank and transaction fee
            bank_transfer_trx.transaction_link_id = fee_trx.id
            fee_trx.transaction_link_id = bank_transfer_trx.id
            db.session.commit()
        # end if

        # send queue here
        result = BankTask().bank_transfer.apply_async(
            args=[bank_transfer_trx.payment.id],
            queue="bank"
        )
        return accepted({"id": str(bank_transfer_trx.id)})
    #end def

    def checkout(self, phone_ext, phone_number):
        """
            Checkout Transfer
            exchange phone number and return wallet available for that users
        """
        user = User.query.filter_by(phone_ext=phone_ext,
                                    phone_number=phone_number).first()
        if user is None:
            raise RequestNotFound(self.error_response["USER_NOT_FOUND"]["TITLE"],
                                  self.error_response["USER_NOT_FOUND"]["MESSAGE"])
        #end if

        # serialize
        user_info = UserSchema(
            only=('name', 'msisdn','wallets.id', 'wallets.status')
        ).dump(user).data
        return ok(user_info)
    #end def

    ################################## PATCH ############################################
    def checkout2(self, phone_ext, phone_number):
        """
            Checkout Transfer
            exchange phone number and return wallet available for that users
        """
        user = User.query.filter_by(phone_ext=phone_ext,
                                    phone_number=phone_number).first()
        if user is None:
            raise RequestNotFound(self.error_response["USER_NOT_FOUND"]["TITLE"],
                                  self.error_response["USER_NOT_FOUND"]["MESSAGE"])
        #end if

        # serialize
        user_info = UserSchema().dump(user).data
        return ok(user_info)
    #end def
#end class
