"""
    Test Authentication Services
"""
import pytest
import uuid
from unittest.mock import patch
from unittest.mock import Mock

from app.api.models import User

from app.api.auth.modules.auth_services import Token, AuthServices

from app.api.auth.exceptions import (
    RevokedTokenError,
    SignatureExpiredError,
    InvalidTokenError,
    EmptyPayloadError,
)

from app.lib.http_error import *

"""
    TEST TOKEN
"""


def test_create(setup_user_only):
    """ test Token class method that generate token """
    user = User.query.filter_by(username="dummyuser").first()
    token = Token.create(user, "ACCESS")
    assert type(token) == str

    token = Token.create(user, "REFRESH")
    assert type(token) == str


def test_decode(setup_user_only):
    """ test Token class method that decode token """
    user = User.query.filter_by(username="dummyuser").first()
    token = Token.create(user, "ACCESS")
    assert type(token) == str

    payload = Token(token).decode()
    assert type(payload) == dict


@patch.object(User, "decode_token")
def test_decode_revoked_token(mock_decode):
    """ test Token class method that decode token using revoked token """
    mock_decode.side_effect = RevokedTokenError
    # TEST INVALID TOKEN
    invalid_token = "eyJhbGciOiJIIzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwidHlwZSI6IkFDQ0VTUyJ9.9JeY4v711wDsUzczKNlR84IMTTab5KwraY4rlQ3jaAQ"
    result = Token(invalid_token).decode()
    assert result == "REVOKED_TOKEN"


@patch.object(User, "decode_token")
def test_decode_signature_expired(mock_decode):
    """ test Token class method that decode token using revoked token """
    mock_decode.side_effect = SignatureExpiredError(Mock())
    # TEST INVALID TOKEN
    invalid_token = "eyJhbGciOiJIIzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwidHlwZSI6IkFDQ0VTUyJ9.9JeY4v711wDsUzczKNlR84IMTTab5KwraY4rlQ3jaAQ"
    result = Token(invalid_token).decode()
    assert result == "SIGNATURE_EXPIRED"


@patch.object(User, "decode_token")
def test_decode_invalid_token(mock_decode):
    """ test Token class method that decode token using invalid token """
    mock_decode.side_effect = InvalidTokenError(Mock())
    # TEST INVALID TOKEN
    invalid_token = "eyJhbGciOiJIIzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwidHlwZSI6IkFDQ0VTUyJ9.9JeY4v711wDsUzczKNlR84IMTTab5KwraY4rlQ3jaAQ"
    result = Token(invalid_token).decode()
    assert result == "INVALID_TOKEN"


@patch.object(User, "decode_token")
def test_decode_empty_payload(mock_decode):
    """ test Token class method that decode token using empty payload token """
    mock_decode.side_effect = EmptyPayloadError(Mock())
    # TEST INVALID TOKEN
    invalid_token = "eyJhbGciOiJIIzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwidHlwZSI6IkFDQ0VTUyJ9.9JeY4v711wDsUzczKNlR84IMTTab5KwraY4rlQ3jaAQ"
    result = Token(invalid_token).decode()
    assert result == "EMPTY_PAYLOAD"


"""
    TEST AUTH SERVICES
"""


def test_current_login_user(setup_user_factory):
    """ test curren login user"""
    setup_user_factory("loggeduser")
    user = User.query.filter_by(username="loggeduser").first()
    token = Token.create(user, "ACCESS")

    result = AuthServices().current_login_user(token)
    assert result["token_type"]
    assert result["user"]


@patch.object(Token, "decode")
def test_current_login_user_mock_token(mock_decode):
    """ test curren login user"""
    mock_decode.return_value = "INVALID_TOKEN"

    with pytest.raises(Unauthorized):
        AuthServices().current_login_user("jaskdjlasjdkljaksldnasndkalsdl")

    mock_decode.return_value = "EMPTY_PAYLOAD"

    with pytest.raises(Unauthorized):
        AuthServices().current_login_user("jaskdjlasjdkljaksldnasndkalsdl")


def test_create_token_success():
    """ test success create access & refresh token"""
    result = AuthServices().create_token(
        {"username": "dummyuser", "password": "password"}
    )
    result = result[0]["data"]

    assert result["access_token"]
    assert result["refresh_token"]


def test_create_token_failed_not_found():
    """ test failed create access & refresh token because user is not
    created yet"""
    with pytest.raises(RequestNotFound):
        AuthServices().create_token({"username": "roserose", "password": "password"})


def test_create_token_failed_incorrect_login():
    """ test failed create access & refresh token by using invalid
    credentials"""
    with pytest.raises(Unauthorized):
        AuthServices().create_token({"username": "dummyuser", "password": "pasword"})


def test_refresh_token_success():
    """ test success refreshing token"""

    user = User.query.filter_by(username="dummyuser").first()
    result = AuthServices().refresh_token(user)
    result = result[0]["data"]
    assert result["access_token"]


def test_check_key():
    """ test check api key"""
    result = AuthServices.check_key("8c574c41-3e01-4763-89af-fd370989da33")
    assert isinstance(result, object)

    with pytest.raises(Unauthorized):
        result = AuthServices.check_key(str(uuid.uuid4()))


def test_blacklist(setup_user_only):
    """ test Token class method that blacklist token """
    user = User.query.filter_by(username="dummyuser").first()
    token = Token.create(user, "ACCESS")

    result = Token(token).blacklist()
    assert result


def test_logout():
    """ test blacklist access token """
    result = AuthServices().create_token(
        {"username": "dummyuser", "password": "password"}
    )
    result = result[0]["data"]
    access_token = result["access_token"]

    result = AuthServices().logout(access_token)
    assert result[1] == 204  # no content
