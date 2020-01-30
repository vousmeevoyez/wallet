"""
    Test Decorator
"""
# pylint: disable=import-error
# pylint: disable=unused-import

import pytest

import uuid
from unittest.mock import patch, Mock

# import all decorator
from app.api.auth.decorator import *
from app.api.auth.decorator import _parse_token
from app.api.auth.decorator import _parse_key

from app.api.auth.exceptions import (
    RevokedTokenError,
    SignatureExpiredError,
    InvalidTokenError,
)

from app.lib.http_error import *


@patch("flask_restplus.reqparse.RequestParser.parse_args")
def test_parse_token(parse_args_mock):
    """ test parse token and return token """
    parse_args_mock.return_value = {"Authorization": "Bearer some_token"}

    result = _parse_token()
    assert result == "some_token"


@patch("flask_restplus.reqparse.RequestParser.parse_args")
def test_parse_token_empty(parse_args_mock):
    """ test parse token and return token """
    parse_args_mock.return_value = {"Authorization": ""}

    with pytest.raises(ParseError):
        _parse_token()


@patch("flask_restplus.reqparse.RequestParser.parse_args")
def test_parse_token_failed(parse_args_mock):
    """ test parse token and return token """
    parse_args_mock.return_value = {"Authorization": "jlkajsdljalsjldjas"}

    with pytest.raises(ParseError):
        _parse_token()


@patch("flask_restplus.reqparse.RequestParser.parse_args")
def test_admin_required_failed(parse_args_mock):
    """ test admin required decorator with invalid token"""
    func = Mock()

    decorated_func = admin_required(func)

    parse_args_mock.return_value = {"Authorization": "jlkajsdljalsjldjas"}

    with pytest.raises(BadRequest):
        decorated_func()


@patch("flask_restplus.reqparse.RequestParser.parse_args")
def test_admin_required_invalid_identifier(parse_args_mock):
    """ test admin required decorator with valid token but invalid user """
    func = Mock()

    decorated_func = admin_required(func)

    parse_args_mock.return_value = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwidHlwZSI6IkFDQ0VTUyJ9.7qJycMO9pCUr9VwQZolkko_Ft0EcOVbwWFlkBOfuKVE"
    }

    with pytest.raises(BadRequest):
        result = decorated_func()


@patch("flask_restplus.reqparse.RequestParser.parse_args")
def test_refresh_token_only(parse_args_mock, setup_user_token_factory):
    """ test refresh token only but with access token"""
    token = setup_user_token_factory("anotherloggeduser")

    func = Mock()

    decorated_func = refresh_token_only(func)

    parse_args_mock.return_value = {"Authorization": "Bearer {}".format(token)}

    with pytest.raises(MethodNotAllowed):
        result = decorated_func()


@patch("flask_restplus.reqparse.RequestParser.parse_args")
def test_token_required(parse_args_mock, setup_user_token_factory):
    """ test get token """
    token = setup_user_token_factory("anotherloggeduser")
    func = Mock()

    decorated_func = token_required(func)

    parse_args_mock.return_value = {"Authorization": "Bearer {}".format(token)}

    result = decorated_func()


@patch("flask_restplus.reqparse.RequestParser.parse_args")
def test_get_token_payload(parse_args_mock, setup_user_token_factory):
    """ test get token """
    token = setup_user_token_factory("anotherloggeduser")
    parse_args_mock.return_value = {"Authorization": "Bearer {}".format(token)}

    result = get_token_payload()
    assert result["token_type"]
    assert result["user"]


@patch("flask_restplus.reqparse.RequestParser.parse_args")
def test_get_current_token(parse_args_mock, setup_user_token):
    """ test get token """
    token = setup_user_token

    parse_args_mock.return_value = {"Authorization": "Bearer {}".format(token)}

    result = get_current_token()
    assert result == token


@patch("flask_restplus.reqparse.RequestParser.parse_args")
def test_parse_key(parse_args_mock):
    """ test get token """
    # empty api key
    parse_args_mock.return_value = {"X-Api-Key": ""}

    with pytest.raises(ParseError):
        result = _parse_key()


@patch("flask_restplus.reqparse.RequestParser.parse_args")
def test_api_key_required_failed(parse_args_mock):
    """ test api keye required decorator """
    func = Mock()

    decorated_func = api_key_required(func)

    parse_args_mock.return_value = {"X-Api-Key": ""}

    with pytest.raises(BadRequest):
        result = decorated_func()
    # end with

    func = Mock()

    decorated_func = api_key_required(func)

    # using invalid api key
    fake_api_key = str(uuid.uuid4())

    parse_args_mock.return_value = {"X-Api-Key": "{}".format(fake_api_key)}

    with pytest.raises(Unauthorized):
        result = decorated_func()
