"""
    Test Decorator
"""
# pylint: disable=import-error
# pylint: disable=unused-import
import uuid
from unittest import mock
from unittest.mock import patch, Mock

from app.api import db

from app.test.base import BaseTestCase
from app.api.models import *

from app.api.auth.modules.auth_services import AuthServices

# import all decorator
from app.api.auth.decorator import *
from app.api.auth.decorator import _parse_token
from app.api.auth.decorator import _parse_key

from app.api.error.authentication import RevokedTokenError
from app.api.error.authentication import SignatureExpiredError
from app.api.error.authentication import InvalidTokenError

from app.api.error.http import *

# import all routes


class TestAuthDecorator(BaseTestCase):
    """ test auth decorator"""

    def _create_dummy_token(self):
        """ test encode a token"""
        # create user role first
        role = Role(description="USER")
        db.session.add(role)
        db.session.commit()

        # create dummy user
        user = User(
            username="lisabp",
            name="lisa",
            email="lisa@bp.com",
            phone_ext="62",
            phone_number="81219644314",
            role_id=role.id,
        )
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        token = user.encode_token("ACCESS", user.id)
        return token.decode()

    # end def

    @mock.patch("flask_restplus.reqparse.RequestParser.parse_args")
    def test_parse_token(self, parse_args_mock):
        """ test parse token and return token """
        parse_args_mock.return_value = {"Authorization": "Bearer some_token"}

        result = _parse_token()
        self.assertEqual(result, "some_token")

    @mock.patch("flask_restplus.reqparse.RequestParser.parse_args")
    def test_parse_token_empty(self, parse_args_mock):
        """ test parse token and return token """
        parse_args_mock.return_value = {"Authorization": ""}

        with self.assertRaises(ParseError):
            result = _parse_token()

    @mock.patch("flask_restplus.reqparse.RequestParser.parse_args")
    def test_parse_token_failed(self, parse_args_mock):
        """ test parse token and return token """
        parse_args_mock.return_value = {"Authorization": "jlkajsdljalsjldjas"}

        with self.assertRaises(ParseError):
            result = _parse_token()

    @mock.patch("flask_restplus.reqparse.RequestParser.parse_args")
    def test_admin_required_failed(self, parse_args_mock):
        """ test admin required decorator with invalid token"""
        func = Mock()

        decorated_func = admin_required(func)

        parse_args_mock.return_value = {"Authorization": "jlkajsdljalsjldjas"}

        with self.assertRaises(BadRequest):
            result = decorated_func()

    @mock.patch("flask_restplus.reqparse.RequestParser.parse_args")
    def test_admin_required_invalid_identifier(self, parse_args_mock):
        """ test admin required decorator with valid token but invalid user """
        func = Mock()

        decorated_func = admin_required(func)

        parse_args_mock.return_value = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwidHlwZSI6IkFDQ0VTUyJ9.7qJycMO9pCUr9VwQZolkko_Ft0EcOVbwWFlkBOfuKVE"
        }

        with self.assertRaises(BadRequest):
            result = decorated_func()

    @mock.patch("flask_restplus.reqparse.RequestParser.parse_args")
    def test_refresh_token_only(self, parse_args_mock):
        """ test refresh token only but with access token"""
        token = self._create_dummy_token()

        func = Mock()

        decorated_func = refresh_token_only(func)

        parse_args_mock.return_value = {"Authorization": "Bearer {}".format(token)}

        with self.assertRaises(MethodNotAllowed):
            result = decorated_func()

    @mock.patch("flask_restplus.reqparse.RequestParser.parse_args")
    def test_token_required(self, parse_args_mock):
        """ test get token """
        token = self._create_dummy_token()
        func = Mock()

        decorated_func = token_required(func)

        parse_args_mock.return_value = {"Authorization": "Bearer {}".format(token)}

        result = decorated_func()

    @mock.patch("flask_restplus.reqparse.RequestParser.parse_args")
    def test_get_token_payload(self, parse_args_mock):
        """ test get token """
        token = self._create_dummy_token()
        parse_args_mock.return_value = {"Authorization": "Bearer {}".format(token)}

        result = get_token_payload()
        self.assertTrue(result["token_type"])
        self.assertTrue(result["user"])

    @mock.patch("flask_restplus.reqparse.RequestParser.parse_args")
    def test_get_current_token(self, parse_args_mock):
        """ test get token """
        token = self._create_dummy_token()

        parse_args_mock.return_value = {"Authorization": "Bearer {}".format(token)}

        result = get_current_token()
        self.assertEqual(result, token)

    @mock.patch("flask_restplus.reqparse.RequestParser.parse_args")
    def test_parse_key(self, parse_args_mock):
        """ test get token """
        # empty api key
        parse_args_mock.return_value = {"X-Api-Key": ""}

        with self.assertRaises(ParseError):
            result = _parse_key()

    @mock.patch("flask_restplus.reqparse.RequestParser.parse_args")
    def test_api_key_required_failed(self, parse_args_mock):
        """ test api keye required decorator """
        func = Mock()

        decorated_func = api_key_required(func)

        parse_args_mock.return_value = {"X-Api-Key": ""}

        with self.assertRaises(BadRequest):
            result = decorated_func()
        # end with

        func = Mock()

        decorated_func = api_key_required(func)

        # using invalid api key
        fake_api_key = str(uuid.uuid4())

        parse_args_mock.return_value = {"X-Api-Key": "{}".format(fake_api_key)}

        with self.assertRaises(Unauthorized):
            result = decorated_func()
