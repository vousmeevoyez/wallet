"""
    Test Wallet Core
"""
import uuid
from unittest.mock import patch, Mock
from app.api import db

from app.test.base  import BaseTestCase

from app.api.models import *

from app.api.wallets.modules.wallet_core import WalletCore

# exceptions
from app.api.error.http import *

fake_wallet_id = str(uuid.uuid4())

class TestWalletCore(BaseTestCase):
    """ Test Class for wallet core """

    def setUp(self):
        super().setUp()

        source_wallet = Wallet(user_id=self.user.id)
        source_wallet.set_pin("123456")
        db.session.add(source_wallet)
        db.session.commit()

        source_wallet.add_balance(1000)
        db.session.flush()

        # create destination wallet secondly
        destination_wallet = Wallet()
        destination_wallet.set_pin("123456")
        db.session.add(destination_wallet)
        db.session.commit()

        self.source = source_wallet
        self.destination = destination_wallet

    def test_wallet_core(self):
        """ test wallet core normal case"""
        result = WalletCore(str(self.source.id), "123456",
                            str(self.destination.id))
        expected_result = {
            "source" : self.source,
            "destination" : self.destination
        }
        self.assertTrue(isinstance(result, object))
        self.assertEqual(result.__dict__, expected_result)

    def test_wallet_core_incorrect_pin(self):
        """ test wallet core for incorrect pin"""
        # fist attempt
        with self.assertRaises(UnprocessableEntity):
            result = WalletCore(str(self.source.id), "000000",
                                str(self.destination.id))

        # second attempt
        with self.assertRaises(UnprocessableEntity):
            result = WalletCore(str(self.source.id), "000000",
                                str(self.destination.id))

        # third attempt
        with self.assertRaises(UnprocessableEntity):
            result = WalletCore(str(self.source.id), "000000",
                                str(self.destination.id))

        # max attempt
        with self.assertRaises(UnprocessableEntity):
            result = WalletCore(str(self.source.id), "000000",
                                str(self.destination.id))

        # wallet locked
        with self.assertRaises(UnprocessableEntity):
            result = WalletCore(str(self.source.id), "000000",
                                str(self.destination.id))


    def test_wallet_core_invalid_destination(self):
        """ test wallet core for invalid wallet destination """
        with self.assertRaises(RequestNotFound):
            result = WalletCore(str(self.source.id), "123456",
                                fake_wallet_id)

    def test_wallet_core_destination_locked(self):
        """ test wallet core for locked wallet destination """
        # lock destination wallet
        self.destination.lock()

        with self.assertRaises(UnprocessableEntity):
            result = WalletCore(str(self.source.id), "123456",
                                str(self.destination.id))

    def test_wallet_core_same_destination(self):
        """ test wallet core for same destination wallet self = destination """
        with self.assertRaises(UnprocessableEntity):
            result = WalletCore(str(self.source.id), "123456",
                                str(self.source.id))
