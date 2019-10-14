"""
    Test Wallet Services
"""
import pytest

from unittest.mock import patch, Mock
from app.api import db

from app.api.models import User, Wallet, ForgotPin, IncorrectPin

from app.api.utility.utils import Sms

from app.api.error.http import *

from app.api.utility.utils import UtilityError

from app.api.wallets.modules.wallet_services import WalletServices


def test_wallet_owner_info(setup_wallet_info):
    result = WalletServices(setup_wallet_info["id"]).owner_info()[0]
    assert result["data"]


def test_add_wallet(setup_wallet_info):
    """ test method for creating wallet"""
    assert setup_wallet_info["id"]


def test_show_wallet(setup_user_wallet_va):
    """ test show wallet """
    access_token, user_id, wallet_id = setup_user_wallet_va

    user = User.query.filter_by(id=user_id).first()

    result = WalletServices.show(user)
    assert len(result) > 0


def test_wallet_info(setup_wallet_info):
    """ test method for get wallet info """
    result = WalletServices(setup_wallet_info["id"]).info()[0]
    assert result["data"]


def test_wallet_info_failed_invalid_id():
    """ test method for get wallet info but not found """
    with pytest.raises(BadRequest):
        WalletServices("1234").info()


def test_wallet_remove_failed_only_wallet(setup_wallet_info2):
    """ test method for removing wallet but failed because wallet can't be
    less than zero """
    with pytest.raises(UnprocessableEntity):
        WalletServices(setup_wallet_info2["id"]).remove()


def test_wallet_update_pin(setup_wallet_info2):
    """ test checking wallet balance"""
    params = {"old_pin": "123456", "pin": "111111", "confirm_pin": "111111"}

    result = WalletServices(setup_wallet_info2["id"], "123456").update_pin(params)
    assert result[1] == 204

    result = WalletServices(setup_wallet_info2["id"], "111111").check()
    assert result[0]["data"]["message"] == "PIN VERIFIED"


def test_wallet_check_pin(setup_wallet_info2):
    """ test checking wallet balance"""
    result = WalletServices(setup_wallet_info2["id"], "111111").check()
    assert result[0]["data"]["message"] == "PIN VERIFIED"

    with pytest.raises(UnprocessableEntity):
        result = WalletServices(setup_wallet_info2["id"], "113456").check()

    with pytest.raises(UnprocessableEntity):
        result = WalletServices(setup_wallet_info2["id"], "000000").check()

    with pytest.raises(UnprocessableEntity):
        result = WalletServices(setup_wallet_info2["id"], "000000").check()

    with pytest.raises(UnprocessableEntity):
        result = WalletServices(setup_wallet_info2["id"], "000000").check()

    db.session.query(IncorrectPin).delete()
    db.session.commit()


def test_wallet_balance(setup_wallet_info):
    """ test checking wallet balance"""
    result = WalletServices(setup_wallet_info["id"]).check_balance()[0]["data"]
    assert result["balance"]


def test_wallet_not_found():
    """ test method for checking wallet balance but not found"""
    with pytest.raises(BadRequest):
        WalletServices("123456").check_balance()


@patch.object(Sms, "send")
def test_send_forgot_otp_success(mock_send_sms, setup_wallet_info):
    """ test method for sending forgot otp sms """
    mock_send_sms.return_value = "test"

    result = WalletServices(setup_wallet_info["id"]).send_forgot_otp()
    assert result[0]["data"]["otp_key"]
    assert result[0]["data"]["otp_code"]

    pytest.otp_key = result[0]["data"]["otp_key"]
    pytest.otp_code = result[0]["data"]["otp_code"]


def test_send_forgot_otp_failed_wallet_not_found(setup_wallet_info):
    """ test method for sending forgot otp sms but wallet id is not found"""
    with pytest.raises(BadRequest):
        WalletServices("1234").send_forgot_otp()


@patch.object(Sms, "send")
def test_send_forgot_otp_failed_pending(mock_send_sms, setup_wallet_info):
    """ test method for sending forgot otp sms but there's still pending
    request"""
    with pytest.raises(UnprocessableEntity):
        result = WalletServices(setup_wallet_info["id"]).send_forgot_otp()


@patch.object(Sms, "send")
def test_send_forgot_otp_failed_raise_sms_error(mock_send_sms, setup_wallet_info):
    """ test method for sending forgot otp sms but there's an error when
    sending the message """
    mock_send_sms.side_effect = UtilityError(Mock())
    with pytest.raises(UnprocessableEntity):
        WalletServices(setup_wallet_info["id"]).send_forgot_otp()


def test_get_qr(setup_wallet_info):
    """ test method to generate qr code wallet """
    result = WalletServices(setup_wallet_info["id"]).get_qr()[0]["data"]
    assert result["qr_string"]


def test_verify_forgot_otp(setup_wallet_info):
    """ test method for sending forgot otp sms """
    result = WalletServices(setup_wallet_info["id"]).verify_forgot_otp(
        {"otp_code": pytest.otp_code, "otp_key": pytest.otp_key, "pin": "111111"}
    )
    assert result[1] == 204


def test_verify_forgot_otp_but_already_verified(setup_wallet_info):
    """ test method for sending forgot otp sms but already veirfied"""
    with pytest.raises(UnprocessableEntity):
        WalletServices(setup_wallet_info["id"]).verify_forgot_otp(
            {"otp_code": pytest.otp_code, "otp_key": pytest.otp_key, "pin": "111111"}
        )

def test_verify_forgot_otp_but_invalid_otp_code(setup_wallet_info):
    """ test method for sending forgot otp sms but already veirfied"""
    with pytest.raises(UnprocessableEntity):
        WalletServices(setup_wallet_info["id"]).verify_forgot_otp(
            {"otp_code": "000000", "otp_key": pytest.otp_key, "pin": "111111"}
        )

def test_verify_forgot_otp_but_invalid_otp_key(setup_wallet_info):
    """ test method for sending forgot otp sms but already veirfied"""
    with pytest.raises(RequestNotFound):
        WalletServices(setup_wallet_info["id"]).verify_forgot_otp(
            {"otp_code": pytest.otp_code, "otp_key": "46464654654654", "pin": "111111"}
        )
