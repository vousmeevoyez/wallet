"""
    This is Celery Task to help interacting with Bank API
    in the background
"""
import random

from flask import current_app
from sqlalchemy.exc import OperationalError, IntegrityError
from celery.exceptions import MaxRetriesExceededError, Reject, Retry

from app.api import celery, sentry, db

from app.api.models import VirtualAccount, Payment, BankAccount

from task.bank.BNI.va import VirtualAccount as VaServices
from task.bank.BNI.va import ApiError as BniVaApiError

from task.bank.BNI.core import CoreBank
from task.bank.BNI.core import ApiError as BniCoreApiError

# config
from app.config.external.bank import BNI_OPG
from app.api.const import WORKER, STATUS


def backoff(attempts):
    """ prevent hammering service with thousand retry"""
    return random.uniform(2, 4) ** attempts


class BankTask(celery.Task):
    """Abstract base class for all tasks in my app."""

    abstract = True

    current_user = None

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Log the exceptions to sentry at retry."""
        sentry.captureException(exc)
        super(BankTask, self).on_retry(exc, task_id, args, kwargs, einfo)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Log the exceptions to sentry."""
        sentry.captureException(exc)
        # end with
        super(BankTask, self).on_failure(exc, task_id, args, kwargs, einfo)

    @celery.task(bind=True)
    def health_check(self, text):
        return text

    """
        BNI VIRTUAL ACCOUNT TASK
    """

    @celery.task(
        bind=True,
        max_retries=int(WORKER["MAX_RETRIES"]),
        task_soft_time_limit=WORKER["SOFT_LIMIT"],
        task_time_limit=WORKER["SOFT_LIMIT"],
        acks_late=WORKER["ACKS_LATE"],
    )
    def create_va(self, virtual_account_id):
        """ create task in background to create a Virtual account """
        # fetch va object
        virtual_account = VirtualAccount.query.filter_by(id=virtual_account_id).first()

        # build phone number
        phone_ext = virtual_account.wallet.user.phone_ext
        phone_number = virtual_account.wallet.user.phone_number
        msisdn = str(phone_ext) + str(phone_number)

        va_payload = {
            "virtual_account": virtual_account.account_no,
            "transaction_id": virtual_account.trx_id,
            "amount": int(virtual_account.amount),
            "customer_name": virtual_account.name,
            "customer_phone": msisdn,
            "datetime_expired": virtual_account.datetime_expired,
        }
        resources = virtual_account.va_type.key
        try:
            result = VaServices(resources).create_va(va_payload)
        except BniVaApiError as error:
            # set current user to wallet id so when something wrong we know exactly what happen
            self.current_user = virtual_account.wallet.id
            self.retry(countdown=backoff(self.request.retries), exc=error)
        # end try

        # update virtual account status to database
        virtual_account.status = STATUS["ACTIVE"]
        db.session.commit()

    """
        BNI CORE BANK
    """

    @celery.task(
        bind=True,
        max_retries=int(WORKER["MAX_RETRIES"]),
        task_soft_time_limit=WORKER["SOFT_LIMIT"],
        task_time_limit=WORKER["SOFT_LIMIT"],
        acks_late=WORKER["ACKS_LATE"],
    )
    def bank_transfer(self, payment_id):
        # fix circular import!
        from app.api.transactions.modules.transaction_services import (
            TransactionServices
        )

        payment = Payment.query.filter_by(id=payment_id).first()

        bank_account_no = payment.to
        # get bank account information
        bank_account = BankAccount.query.filter_by(
            account_no=bank_account_no
        ).first()

        # convert amount to positive
        amount = abs(int(payment.amount))

        transfer_payload = {
            "amount": amount,  # BANK CODE
            "bank_code": bank_account.bank.code,  # BANK CODE
            "source_account": BNI_OPG["MASTER_ACCOUNT"],  # MASTER ACCOUNT ID
            "account_no": bank_account_no,  # destination account bank transfer
            "ref_number": None,  # use system generated refnumber
        }

        try:
            result = CoreBank().transfer(transfer_payload)
        except BniCoreApiError as error:
            # handle celery exception here
            try:
                # set current user to wallet id so when something wrong we know exactly what happen
                self.current_user = payment.source_account
                self.retry(countdown=backoff(self.request.retries))
            except MaxRetriesExceededError:
                # create transaction refund here
                transaction_id = str(payment.transaction.id)
                result = TransactionServices(
                    transaction_id=transaction_id
                ).refund()
                current_app.logger.info("REFUND {}".format(result))
        else:
            # get reference number from transfer response
            transfer_info = result["data"]["transfer_info"]
            # update referenc number here
            request_reference = transfer_info["ref_number"]
            # try fetch bank reference if available
            response_reference = transfer_info.get("bank_ref", "NA")
            payment.ref_number = request_reference + "-" + response_reference
            db.session.commit()
        finally:
            # only enable the fake callback when it is debug
            if current_app.debug:
                import grpc
                from task.bank.lib.rpc import callback_pb2
                from task.bank.lib.rpc import callback_pb2_grpc
                # send fake callback via gRPC
                channel = grpc.insecure_channel("callback:10000")
                stub = callback_pb2_grpc.CallbackStub(channel)
                request = callback_pb2.DepositCallbackRequest()
                request.body.virtual_account = bank_account_no
                request.body.payment_amount = str(amount)
                try:
                    response = stub.DepositCallback(request)
                except grpc.RpcError as error:
                    current_app.logger.warning(error.code())
                    current_app.logger.warning(error.details())
                # end try
                current_app.logger.info(response)
        # end try
