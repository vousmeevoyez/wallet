"""
    Test Authentication Services
"""

import uuid
from unittest.mock import patch
from unittest.mock import Mock

from app.test.base import BaseTestCase
from app.api.models import User

from app.api.auth.modules.auth_services import Token, AuthServices

from app.api.error.authentication import RevokedTokenError
from app.api.error.authentication import SignatureExpiredError
from app.api.error.authentication import InvalidTokenError
from app.api.error.authentication import EmptyPayloadError

from app.api.error.http import *


class TestToken(BaseTestCase):
    def test_create(self):
        """ test Token class method that generate token """
        user = User.query.filter_by(username="MODANAADMIN").first()
        token = Token.create(user, "ACCESS")
        self.assertIsInstance(token, str)

        token = Token.create(user, "REFRESH")
        self.assertIsInstance(token, str)

    def test_decode(self):
        """ test Token class method that decode token """
        user = User.query.filter_by(username="MODANAADMIN").first()
        token = Token.create(user, "ACCESS")

        payload = Token(token).decode()
        self.assertIsInstance(payload, dict)

    @patch.object(User, "decode_token")
    def test_decode_revoked_token(self, mock_decode):
        """ test Token class method that decode token using revoked token """
        mock_decode.side_effect = RevokedTokenError
        # TEST INVALID TOKEN
        invalid_token = "eyJhbGciOiJIIzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwidHlwZSI6IkFDQ0VTUyJ9.9JeY4v711wDsUzczKNlR84IMTTab5KwraY4rlQ3jaAQ"
        result = Token(invalid_token).decode()
        self.assertEqual(result, "REVOKED_TOKEN")

    @patch.object(User, "decode_token")
    def test_decode_signature_expired(self, mock_decode):
        """ test Token class method that decode token using revoked token """
        mock_decode.side_effect = SignatureExpiredError(Mock())
        # TEST INVALID TOKEN
        invalid_token = "eyJhbGciOiJIIzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwidHlwZSI6IkFDQ0VTUyJ9.9JeY4v711wDsUzczKNlR84IMTTab5KwraY4rlQ3jaAQ"
        result = Token(invalid_token).decode()
        self.assertEqual(result, "SIGNATURE_EXPIRED")

    @patch.object(User, "decode_token")
    def test_decode_invalid_token(self, mock_decode):
        """ test Token class method that decode token using invalid token """
        mock_decode.side_effect = InvalidTokenError(Mock())
        # TEST INVALID TOKEN
        invalid_token = "eyJhbGciOiJIIzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwidHlwZSI6IkFDQ0VTUyJ9.9JeY4v711wDsUzczKNlR84IMTTab5KwraY4rlQ3jaAQ"
        result = Token(invalid_token).decode()
        self.assertEqual(result, "INVALID_TOKEN")

    @patch.object(User, "decode_token")
    def test_decode_empty_payload(self, mock_decode):
        """ test Token class method that decode token using empty payload token """
        mock_decode.side_effect = EmptyPayloadError(Mock())
        # TEST INVALID TOKEN
        invalid_token = "eyJhbGciOiJIIzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwidHlwZSI6IkFDQ0VTUyJ9.9JeY4v711wDsUzczKNlR84IMTTab5KwraY4rlQ3jaAQ"
        result = Token(invalid_token).decode()
        self.assertEqual(result, "EMPTY_PAYLOAD")

    def test_blacklist(self):
        """ test Token class method that blacklist token """
        user = User.query.filter_by(username="MODANAADMIN").first()
        token = Token.create(user, "ACCESS")

        result = Token(token).blacklist()
        self.assertTrue(result)


class TestAuthServices(BaseTestCase):
    """ test auth services class"""

    def test_current_login_user(self):
        """ test curren login user"""
        user = User.query.filter_by(username="MODANAADMIN").first()
        token = Token.create(user, "ACCESS")

        result = AuthServices().current_login_user(token)
        self.assertIsInstance(result, dict)

    @patch.object(Token, "decode")
    def test_current_login_user_mock_token(self, mock_decode):
        """ test curren login user"""
        mock_decode.return_value = "INVALID_TOKEN"

        with self.assertRaises(Unauthorized):
            result = AuthServices().current_login_user("jaskdjlasjdkljaksldnasndkalsdl")

        mock_decode.return_value = "EMPTY_PAYLOAD"

        with self.assertRaises(Unauthorized):
            result = AuthServices().current_login_user("jaskdjlasjdkljaksldnasndkalsdl")

    def test_create_token_success(self):
        """ test success create access & refresh token"""
        result = AuthServices().create_token(
            {"username": "MODANAADMIN", "password": "password"}
        )
        result = result[0]["data"]

        self.assertTrue(result["access_token"])
        self.assertTrue(result["refresh_token"])

    def test_create_token_failed_not_found(self):
        """ test failed create access & refresh token because user is not
        created yet"""
        with self.assertRaises(RequestNotFound):
            result = AuthServices().create_token(
                {"username": "roserose", "password": "password"}
            )

    def test_create_token_failed_incorrect_login(self):
        """ test failed create access & refresh token by using invalid
        credentials"""
        with self.assertRaises(Unauthorized):
            result = AuthServices().create_token(
                {"username": "MODANAADMIN", "password": "pasword"}
            )

    def test_refresh_token_success(self):
        """ test success refreshing token"""

        user = User.query.filter_by(username="MODANAADMIN").first()
        result = AuthServices().refresh_token(user)
        result = result[0]["data"]

        self.assertTrue(result["access_token"])

    def test_logout(self):
        """ test blacklist access token """
        result = AuthServices().create_token(
            {"username": "MODANAADMIN", "password": "password"}
        )
        result = result[0]["data"]
        access_token = result["access_token"]
        result = AuthServices().logout(access_token)
        self.assertTrue(result[1], 204)  # no content

    def test_check_key(self):
        """ test check api key"""
        result = AuthServices.check_key("8c574c41-3e01-4763-89af-fd370989da33")
        self.assertTrue(isinstance(result, object))

        with self.assertRaises(Unauthorized):
            result = AuthServices.check_key(str(uuid.uuid4()))
