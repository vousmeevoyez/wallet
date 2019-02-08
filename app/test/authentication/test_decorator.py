"""
    Test Decorator
"""
#pylint: disable=import-error
#pylint: disable=unused-import
from unittest import mock
from unittest.mock import patch, Mock

from app.test.base import BaseTestCase
from app.api.models import User

from app.api.authentication.modules.auth_services   import AuthServices

# import all decorator
from app.api.authentication.decorator import admin_required
from app.api.authentication.decorator import refresh_token_only
from app.api.authentication.decorator import token_required
from app.api.authentication.decorator import get_token_payload
from app.api.authentication.decorator import get_current_token
from app.api.authentication.decorator import _parse_token

from app.api.exception.authentication import TokenError
from app.api.exception.authentication import RevokedTokenError
from app.api.exception.authentication import SignatureExpiredError
from app.api.exception.authentication import InvalidTokenError
from app.api.exception.authentication import ParseTokenError
from app.api.exception.authentication import InvalidAuthorizationError
from app.api.exception.authentication import InsufficientScopeError
from app.api.exception.authentication import MethodNotAllowedError

# import all routes

class TestAuthDecorator(BaseTestCase):
    """ test auth decorator"""

    @mock.patch("flask_restplus.reqparse.RequestParser.parse_args")
    def test_parse_token(self, parse_args_mock):
        """ test parse token and return token """
        parse_args_mock.return_value = {
            "Authorization" : "Bearer some_token"
        }

        result = _parse_token()
        self.assertEqual(result, "some_token")

    @mock.patch("flask_restplus.reqparse.RequestParser.parse_args")
    def test_parse_token_empty(self, parse_args_mock):
        """ test parse token and return token """
        parse_args_mock.return_value = {
            "Authorization" : ""
        }

        with self.assertRaises(ParseTokenError):
            result = _parse_token()

    @mock.patch("flask_restplus.reqparse.RequestParser.parse_args")
    def test_parse_token_failed(self, parse_args_mock):
        """ test parse token and return token """
        parse_args_mock.return_value = {
            "Authorization" : "jlkajsdljalsjldjas"
        }

        with self.assertRaises(ParseTokenError):
            result = _parse_token()

    @mock.patch("flask_restplus.reqparse.RequestParser.parse_args")
    def test_admin_required_failed(self, parse_args_mock):
        """ test admin required decorator with invalid token"""
        func = Mock()

        decorated_func = admin_required(func)

        parse_args_mock.return_value = {
            "Authorization" : "jlkajsdljalsjldjas"
        }

        with self.assertRaises(InvalidAuthorizationError):
            result = decorated_func()

    @mock.patch("flask_restplus.reqparse.RequestParser.parse_args")
    def test_admin_required_invalid_user(self, parse_args_mock):
        """ test admin required decorator with valid token but invalid user """
        func = Mock()

        decorated_func = admin_required(func)

        parse_args_mock.return_value = {
            "Authorization" : "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwidHlwZSI6IkFDQ0VTUyJ9.7qJycMO9pCUr9VwQZolkko_Ft0EcOVbwWFlkBOfuKVE"
        }

        with self.assertRaises(InsufficientScopeError):
            result = decorated_func()

    @mock.patch("flask_restplus.reqparse.RequestParser.parse_args")
    def test_refresh_token_only(self, parse_args_mock):
        """ test refresh token only but with access token"""
        func = Mock()

        decorated_func = refresh_token_only(func)

        parse_args_mock.return_value = {
            "Authorization" : "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiQUNDRVNTIiwic3ViIjoiMSIsInJvbGUiOiJVU0VSIn0.hUmo1KTifwr1Ettj7TqoIdvCM6gXSUBELpW02oPlUj4"
        }

        with self.assertRaises(MethodNotAllowedError):
            result = decorated_func()

    @mock.patch("flask_restplus.reqparse.RequestParser.parse_args")
    def test_token_required(self, parse_args_mock):
        """ test get token """
        func = Mock()

        decorated_func = token_required(func)

        parse_args_mock.return_value = {
            "Authorization" : "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiQUNDRVNTIiwic3ViIjoiMSIsInJvbGUiOiJVU0VSIn0.hUmo1KTifwr1Ettj7TqoIdvCM6gXSUBELpW02oPlUj4"
        }

        result = decorated_func()

    @mock.patch("flask_restplus.reqparse.RequestParser.parse_args")
    def test_get_token_payload(self, parse_args_mock):
        """ test get token """
        parse_args_mock.return_value = {
            "Authorization" : "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiQUNDRVNTIiwic3ViIjoiMSIsInJvbGUiOiJVU0VSIn0.hUmo1KTifwr1Ettj7TqoIdvCM6gXSUBELpW02oPlUj4"
        }

        result = get_token_payload()
        self.assertTrue(result["token_type"])
        self.assertTrue(result["user"])

    @mock.patch("flask_restplus.reqparse.RequestParser.parse_args")
    def test_get_current_token(self, parse_args_mock):
        """ test get token """
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiQUNDRVNTIiwic3ViIjoiMSIsInJvbGUiOiJVU0VSIn0.hUmo1KTifwr1Ettj7TqoIdvCM6gXSUBELpW02oPlUj4"

        parse_args_mock.return_value = {
            "Authorization" : "Bearer {}".format(token)
        }

        result = get_current_token()
        self.assertEqual(result, token)
