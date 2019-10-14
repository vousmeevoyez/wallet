"""
    Test Wallet Core
"""
import pytest

import uuid
from unittest.mock import patch, Mock
from app.api import db

from app.api.models import *

from app.api.wallets.modules.wallet_core import WalletCore

# exceptions
from app.api.error.http import *

fake_wallet_id = str(uuid.uuid4())


def test_wallet_core(setup_user_wallet_va,
                     setup_user_wallet_va_without_balance):
    """ test wallet core normal case"""
    source_access_token, source_user_id, source_wallet_id = \
        setup_user_wallet_va
    destination_access_token, destination_user_id, destination_wallet_id = \
        setup_user_wallet_va_without_balance

    result = WalletCore(source_wallet_id, "123456", destination_wallet_id)

    assert isinstance(result, object)
    assert result.__dict__["source"]
    assert result.__dict__["destination"]


def test_wallet_core_incorrect_pin(setup_user_wallet_va,
                                   setup_user_wallet_va_without_balance):
    """ test wallet core for incorrect pin"""
    source_access_token, source_user_id, source_wallet_id = \
        setup_user_wallet_va
    destination_access_token, destination_user_id, destination_wallet_id = \
        setup_user_wallet_va_without_balance

    # fist attempt
    with pytest.raises(UnprocessableEntity):
        result = WalletCore(source_wallet_id, "000000", destination_wallet_id)

    # second attempt
    with pytest.raises(UnprocessableEntity):
        result = WalletCore(source_wallet_id, "000000", destination_wallet_id)

    # third attempt
    with pytest.raises(UnprocessableEntity):
        result = WalletCore(source_wallet_id, "000000", destination_wallet_id)

    # max attempt
    with pytest.raises(UnprocessableEntity):
        result = WalletCore(source_wallet_id, "000000", destination_wallet_id)

    # wallet locked
    with pytest.raises(UnprocessableEntity):
        result = WalletCore(source_wallet_id, "000000", destination_wallet_id)

    wallet = Wallet.query.get(source_wallet_id)
    wallet.unlock()
    db.session.commit()

def test_wallet_core_invalid_destination(setup_user_wallet_va,
                                         setup_user_wallet_va_without_balance):
    """ test wallet core for invalid wallet destination """
    source_access_token, source_user_id, source_wallet_id = \
        setup_user_wallet_va
    destination_access_token, destination_user_id, destination_wallet_id = \
        setup_user_wallet_va_without_balance

    with pytest.raises(RequestNotFound):
        WalletCore(source_wallet_id, "123456", fake_wallet_id)


def test_wallet_core_destination_locked(setup_user_wallet_va,
                                        setup_user_wallet_va_without_balance):
    """ test wallet core for locked wallet destination """
    # lock destination wallet
    source_access_token, source_user_id, source_wallet_id = \
        setup_user_wallet_va
    destination_access_token, destination_user_id, destination_wallet_id = \
        setup_user_wallet_va_without_balance

    wallet = Wallet.query.get(destination_wallet_id)
    wallet.lock()
    db.session.commit()

    with pytest.raises(UnprocessableEntity):
        result = WalletCore(source_wallet_id, "123456", destination_wallet_id)

    wallet.unlock()
    db.session.commit()

def test_wallet_core_same_destination(setup_user_wallet_va,
                                      setup_user_wallet_va_without_balance):
    """ test wallet core for same destination wallet self = destination """
    source_access_token, source_user_id, source_wallet_id = \
        setup_user_wallet_va
    destination_access_token, destination_user_id, destination_wallet_id = \
        setup_user_wallet_va_without_balance

    with pytest.raises(UnprocessableEntity):
        result = WalletCore(source_wallet_id, "123456", source_wallet_id)
