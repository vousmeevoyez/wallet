from app.api.models import Payment, Transaction
from app.api.transactions.factories.transactions.factory import \
generate_transaction
from app.api.transactions.factories.transactions.products import \
TransactionError

from app.api.transactions.factories.payments.factory import generate_payment

from app.api.error.http import UnprocessableEntity
from app.config import config

ERROR_RESPONSE = config.Config.ERROR_CONFIG

def _serialize_object(object_):
    if hasattr(object_, "id"):
        result = object_.id
    else:
        result = object_
    return result

def process_transaction(source, destination, amount, flag, notes=None,
                        channel_id=None, reference_number=None):
    # serialize source & destination here
    source_account = _serialize_object(source)
    to = _serialize_object(destination)

    # generate payment first
    payment = Payment(
        source_account=source_account,
        to=to,
        amount=amount,
        channel_id=channel_id,
        ref_number=reference_number
    )

    # check payment type and set targetted wallet
    payment_type = "CREDIT"
    wallet = destination
    if amount < 0:
        payment_type = "DEBIT"
        wallet = source

    payment = generate_payment(payment, payment_type)
    if payment is None:
        raise UnprocessableEntity(
            ERROR_RESPONSE["DUPLICATE_PAYMENT"]["TITLE"],
            ERROR_RESPONSE["DUPLICATE_PAYMENT"]["MESSAGE"]
        )

    transaction = Transaction(
        wallet=wallet,
        amount=amount,
        notes=notes,
        payment=payment
    )

    try:
        transaction = generate_transaction(transaction, flag)
    except TransactionError as error:
        raise UnprocessableEntity(
            ERROR_RESPONSE["TRANSFER_FAILED"]["TITLE"],
            ERROR_RESPONSE["TRANSFER_FAILED"]["MESSAGE"]
        )
    return transaction
