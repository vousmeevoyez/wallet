from abc import ABC, abstractmethod
from app.api.transactions.factories.transactions.products import (
    TransferTransaction,
    PayrollTransaction,
    WithdrawTransaction,
    BankTransferTransaction,
    TransferFeeTransaction,
    AutoDebitTransaction,
    CreditRefundTransaction,
    AutoPayTransaction,
    TopUpTransaction,
    ReceiveTransferTransaction,
    ReceivePayrollTransaction,
    DebitRefundTransaction,
)


class TransactionFactory:
    """" factory class to help decide what type of transaction should we build """

    def __init__(self):
        self._creators = {}

    # end def

    def register(self, type_, creator):
        """ regist known product """
        self._creators[type_] = creator

    # end def

    def get(self, type_):
        """ get concrete product based on transaction type """
        creator = self._creators.get(type_)
        if not creator:
            raise ValueError(type_)
        return creator()

    # end def


# end class


def generate_transaction(transaction, type_):
    """ interface to generate debit and credit """
    factory = TransactionFactory()
    # regist known transaction here
    # DEBIT TYPE
    factory.register("TRANSFER", TransferTransaction)
    factory.register("PAYROLL", PayrollTransaction)
    factory.register("WITHDRAW", WithdrawTransaction)
    factory.register("BANK_TRANSFER", BankTransferTransaction)
    factory.register("TRANSFER_FEE", TransferFeeTransaction)
    factory.register("AUTO_DEBIT", AutoDebitTransaction)
    factory.register("AUTO_PAY", AutoPayTransaction)
    factory.register("CREDIT_REFUND", DebitRefundTransaction)
    # CREDIT TYPE
    factory.register("TOP_UP", TopUpTransaction)
    factory.register("RECEIVE_TRANSFER", ReceiveTransferTransaction)
    factory.register("RECEIVE_PAYROLL", ReceivePayrollTransaction)
    factory.register("DEBIT_REFUND", CreditRefundTransaction)

    generator = factory.get(type_)
    transaction.load(generator)
    return generator.create(type_)


# end def
