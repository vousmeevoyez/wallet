from app.api        import db

from app.test.base          import BaseTestCase
from app.api.models         import Wallet, Payment
from app.api.wallet.modules import transfer

class TestWalletTransfer(BaseTestCase):

    def test_create_payment(self):
        params = {
            "source"      : "123456",
            "destination" : "123457",
            "amount"      : 12,
            "payment_type": True,
        }
        result = transfer.TransferController()._create_payment(params)
        self.assertTrue(result > 0)

    def test_unlock_lock_account(self):
        wallet  = Wallet()
        wallet2 = Wallet()
        result = transfer.TransferController()._lock_account(wallet, wallet2)
        self.assertTrue(result)

        result = transfer.TransferController()._unlock_account(wallet, wallet2)
        self.assertTrue(result)

    def test_debit_transaction(self):
        wallet = Wallet()
        db.session.add(wallet)
        db.session.flush()
        wallet.add_balance(1000)

        wallet2 = Wallet()
        db.session.add(wallet2)
        db.session.flush()

        #start transaction here
        trx_amount = 10
        # first create debit payment
        debit_payment = Payment(
            source_account=wallet.id,
            to=wallet2.id,
            amount=trx_amount,
            payment_type=False,
        )
        db.session.add(debit_payment)
        db.session.flush()

        result = transfer.TransferController()._debit_transaction(wallet, debit_payment.id, 111)
        self.assertTrue(result)

    def test_credit_transaction(self):
        wallet = Wallet()
        db.session.add(wallet)
        db.session.flush()

        wallet2 = Wallet()
        db.session.add(wallet2)
        db.session.flush()

        #start transaction here
        trx_amount = 10
        # first create debit payment
        credit_payment = Payment(
            source_account=wallet.id,
            to=wallet2.id,
            amount=trx_amount,
            payment_type=True,
        )
        db.session.add(credit_payment)
        db.session.flush()

        result = transfer.TransferController()._credit_transaction(wallet, credit_payment.id, trx_amount)
        self.assertTrue(result)

