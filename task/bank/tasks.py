"""
    This is Celery Task to help interacting with Bank API
    in the background
"""

from app.api import sentry
from app.api import db
from app.api import celery

from app.api.models import *

from task.bank.BNI.helper import VirtualAccount as VaServices
from task.bank.BNI.helper import CoreBank as CoreServices

# exceptions
from task.bank.exceptions.general import *

from app.config import config

TRANSACTION_CONFIG = config.Config.TRANSACTION_CONFIG
TRANSACTION_LOG_CONFIG = config.Config.TRANSACTION_LOG_CONFIG
PAYMENT_STATUS_CONFIG = config.Config.PAYMENT_STATUS_CONFIG
BNI_OPG_CONFIG = config.Config.BNI_OPG_CONFIG
WORKER_CONFIG = config.Config.WORKER_CONFIG
STATUS_CONFIG = config.Config.STATUS_CONFIG

def backoff(attempts):
    """ prevent hammering service with thousand retry"""
    return 2 ** attempts

class TransferFailed(Exception):
    """ raised when something occured on transfer process """

class BankTask(celery.Task):
    """Abstract base class for all tasks in my app."""

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Log the exceptions to sentry at retry."""
        sentry.captureException(exc)
        super(BankTask, self).on_retry(exc, task_id, args, kwargs, einfo)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Log the exceptions to sentry."""
        sentry.captureException(exc)
        super(BankTask, self).on_failure(exc, task_id, args, kwargs, einfo)

    """
        BNI VIRTUAL ACCOUNT TASK 
    """
    @celery.task(bind=True,
                 max_retries=WORKER_CONFIG["MAX_RETRIES"],
                 task_soft_time_limit=WORKER_CONFIG["SOFT_LIMIT"],
                 task_time_limit=WORKER_CONFIG["SOFT_LIMIT"],
                 acks_late=WORKER_CONFIG["ACKS_LATE"],
                )
    def create_va(self, virtual_account_id):
        """ create task in background to create a Virtual account """
        # fetch va object
        virtual_account = VirtualAccount.query.filter_by(id=virtual_account_id).first()

        # build phone number 
        phone_ext =  virtual_account.wallet.user.phone_ext
        phone_number = virtual_account.wallet.user.phone_number
        msisdn = str(phone_ext) + str(phone_number)

        va_payload = {
            "virtual_account" : virtual_account.account_no,
            "transaction_id"  : virtual_account.trx_id,
            "amount"          : int(virtual_account.amount),
            "customer_name"   : virtual_account.name,
            "customer_phone"  : msisdn,
            "datetime_expired": virtual_account.datetime_expired,
        }
        resources = virtual_account.va_type.key
        try:
            result = VaServices().create_va(resources, va_payload)
        except ApiError as error:
            self.retry(countdown=backoff(self.request.retries), exc=error)
        #end try

        # update virtual account status to database
        virtual_account.status = STATUS_CONFIG["ACTIVE"]
        db.session.commit()

    """
        BNI CORE BANK
    """
    @celery.task(bind=True,
                 max_retries=WORKER_CONFIG["MAX_RETRIES"],
                 task_soft_time_limit=WORKER_CONFIG["SOFT_LIMIT"],
                 task_time_limit=WORKER_CONFIG["SOFT_LIMIT"],
                 acks_late=WORKER_CONFIG["ACKS_LATE"],
                )
    def bank_transfer(self, payment_id):
        payment = Payment.query.filter_by(id=payment_id).first()

        bank_account_no = payment.to
        # get bank account information
        bank_account = BankAccount.query.filter_by(account_no=bank_account_no).first()

        transfer_payload = {
            "amount"         : payment.amount, # BANK CODE
            "bank_code"      : bank_account.bank.code, # BANK CODE
            "source_account" : BNI_OPG_CONFIG["MASTER_ACCOUNT"], # MASTER ACCOUNT ID
            "account_no"     : bank_account_no# destination account bank transfer
        }

        try:
            result = CoreServices().transfer(transfer_payload)
        except ApiError as error:
            self.retry(countdown=backoff(self.request.retries), exc=error)
        #end try
        # get reference number from transfer response
        transfer_info = result["data"]["transfer_info"]
        return transfer_info

class TransactionTask(celery.Task):
    """Abstract base class for all tasks in my app."""

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Log the exceptions to sentry at retry."""
        sentry.captureException(exc)
        super(TransactionTask, self).on_retry(exc, task_id, args, kwargs, einfo)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Log the exceptions to sentry."""
        sentry.captureException(exc)
        super(TransactionTask, self).on_failure(exc, task_id, args, kwargs, einfo)

    @celery.task(bind=True,
                 max_retries=WORKER_CONFIG["MAX_RETRIES"],
                 task_soft_time_limit=WORKER_CONFIG["SOFT_LIMIT"],
                 task_time_limit=WORKER_CONFIG["SOFT_LIMIT"],
                 acks_late=WORKER_CONFIG["ACKS_LATE"],
                )
    def transfer(self, payment_id):
        """ create task in background to move money between wallet """
        # fetch payment object
        payment = Payment.query.filter_by(id=payment_id).first()

        # create transaction log for this payment
        log = Log(payment_id=payment.id, state=1)
        db.session.add(log)

        # fetch targe wallet here
        if payment.payment_type is True: # CREDIT
            wallet_id = payment.to
        else: # DEBIT
            wallet_id = payment.source_account

        wallet = Wallet.query.filter_by(id=wallet_id).first()

        # add wallet balance
        wallet.add_balance(payment.amount)

        # commit everything here
        try:
            db.session.commit()
        except IntegrityError as error:
            db.session.rollback()
            sentry.captureException(error)
            # retry the task again
            self.retry(exc=error)
        #end try
    #end def
