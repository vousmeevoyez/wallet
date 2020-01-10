"""
    This is Celery Task to help interacting with Bank API
    in the background
"""
from flask import current_app
from celery.exceptions import (
    MaxRetriesExceededError
)

from app.api import (
    celery,
    sentry,
    db
)
from app.api.models import (
    VirtualAccount,
    Payment,
    BankAccount
)
from app.api.utility.utils import backoff

from task.bank.factories.provider.factory import generate_provider
from task.bank.lib.provider import ProviderError
from task.bank.lib.helper import generate_ref_number

# config
from app.api.const import WORKER, STATUS
from app.config.external.bank import BNI_OPG


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
            "account_no": virtual_account.account_no,
            "trx_id": virtual_account.trx_id,
            "amount": int(virtual_account.amount),
            "customer_name": virtual_account.name,
            "customer_phone": msisdn,
            "expire_date": virtual_account.datetime_expired,
        }
        try:
            provider = generate_provider("BNI_VA")
            provider.set(virtual_account.va_type.key)
            provider.create_va(**va_payload)
        except ProviderError as error:
            # set current user to wallet id so when something wrong we know exactly what happen
            self.current_user = virtual_account.wallet.id
            self.retry(countdown=backoff(self.request.retries), exc=error)
        # end try

        # update virtual account status to database
        virtual_account.status = STATUS["ACTIVE"]
        db.session.commit()

    @celery.task(
        bind=True,
        max_retries=int(WORKER["MAX_RETRIES"]),
        task_soft_time_limit=WORKER["SOFT_LIMIT"],
        task_time_limit=WORKER["SOFT_LIMIT"],
        acks_late=WORKER["ACKS_LATE"],
    )
    def update_va(self, virtual_account_id):
        """ create task in background to create a Virtual account """
        # fetch va object
        virtual_account = VirtualAccount.query.filter_by(
            id=virtual_account_id
        ).first()

        va_payload = {
            "trx_id": virtual_account.trx_id,
            "amount": int(virtual_account.amount),
            "customer_name": virtual_account.name,
            "expire_date": virtual_account.datetime_expired,
        }
        try:
            provider = generate_provider("BNI_VA")
            provider.set(virtual_account.va_type.key)
            provider.update_va(**va_payload)
        except ProviderError as error:
            # set current user to wallet id so when something wrong we know exactly what happen
            self.retry(countdown=backoff(self.request.retries), exc=error)
        # end try
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

        inquiry_ref_number = generate_ref_number(
            bank_account_no
        )

        transfer_ref_number = generate_ref_number(
            bank_account_no, amount
        )

        transfer_payload = {
            "amount": amount,  # BANK CODE
            "bank_code": bank_account.bank.code,  # BANK CODE
            "source": BNI_OPG["MASTER_ACCOUNT"],  # MASTER ACCOUNT ID
            "destination": bank_account_no,  # destination account bank transfer
            "destination_name": bank_account.name,
            "inquiry_ref_number": inquiry_ref_number,
            "transfer_ref_number": transfer_ref_number
        }

        try:
            provider = generate_provider("BNI_OPG")
            result = provider.transfer(transfer_payload)
        except ProviderError as error:
            # handle celery exception here
            # prevent retrying when it is already requested
            if error.message != "DUPLICATE_REQUEST":
                try:
                    # set current user to wallet id so when something wrong we
                    # know exactly what happen
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
                # abort!
                celery.control.revoke(self.request.id)
        else:
            # get reference number from transfer response
            transfer_info = result["transfer_info"]
            # try fetch bank reference if available
            response_reference = transfer_info.get("bank_ref", "NA")
            payment.ref_number = transfer_ref_number + "-" + response_reference
            db.session.commit()
        # clear function cache
        generate_ref_number.cache_clear()
