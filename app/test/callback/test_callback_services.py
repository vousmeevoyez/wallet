import json

from app.test.base  import BaseTestCase
from app.api.models import *

from app.api.callback.modules.callback_services import CallbackServices

class TestCallbackServices(BaseTestCase):
    """ test callback services """
    def _create_wallet(self):
        source_wallet = Wallet()
        source_wallet.set_pin("123456")
        db.session.add(source_wallet)
        db.session.commit()
        return source_wallet

    def _create_va(self):
        wallet = self._create_wallet()

        va_type = VaType.query.filter_by(key="CREDIT").first()

        va = VirtualAccount(wallet_id=wallet.id, va_type_id=va_type.id)

        va_id = va.generate_va_number()
        trx_id = va.generate_trx_id()
        db.session.add(va)
        db.session.commit()

        return va_id, trx_id

    def test_deposit(self):
        """ test deposit """
        virtual_account, trx_id = self._create_va()
        params = {
            "payment_amount" : 10000,
            "payment_ntb" : "123456",
            "payment_channel_key" : "BNI_VA"
        }
        result = CallbackServices(virtual_account, trx_id).deposit(params)

        va = VirtualAccount.query.filter_by(id=virtual_account).first()
        self.assertEqual(va.wallet.balance, 10000)
    #end def
#end class
