"""
    Test Authentication Services
"""

from unittest.mock import patch
from unittest.mock import Mock

from app.test.base import BaseTestCase
from app.api.models import User

from app.api.authentication.modules.auth_services import AuthServices

from app.api.exception.authentication import TokenError
from app.api.exception.authentication import RevokedTokenError
from app.api.exception.authentication import SignatureExpiredError
from app.api.exception.authentication import InvalidTokenError
from app.api.exception.authentication import EmptyPayloadError
from app.api.exception.authentication import InvalidCredentialsError

from app.api.exception.user import UserNotFoundError
from app.api.exception.general import RecordNotFoundError

class TestAuthServices(BaseTestCase):
    """ test auth services class"""

    def test_create_access_token(self):
        """ test create access token """
        user = User.query.filter_by(username="MODANAADMIN").first()
        result = AuthServices()._create_access_token(user)
        self.assertIsInstance(result, str)

    def test_create_refresh_token(self):
        """ test create refresh token"""
        user = User.query.filter_by(username="MODANAADMIN").first()
        result = AuthServices()._create_refresh_token(user)
        self.assertIsInstance(result, str)

    def test_current_login_user(self):
        """ test curren login user"""
        user = User.query.filter_by(username="MODANAADMIN").first()
        token = AuthServices()._create_access_token(user)

        result = AuthServices._current_login_user(token)

        self.assertEqual(result["token_type"], "ACCESS")

    def test_current_login_user_invalid(self):
        """ test curren login user"""
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwidHlwZSI6IkFDQ0VTUyJ9.9JeY4v711wDsUzczKNlR84IMTTab5KwraY4rlQ3jaAQ"
        with self.assertRaises(RecordNotFoundError):
            result = AuthServices._current_login_user(token)

    @patch.object(User, "decode_token")
    def test_current_login_user_revoked_token(self, mock_decode):
        """ test curren login user but using revoked token"""

        mock_decode.side_effect = RevokedTokenError
        with self.assertRaises(TokenError):
            AuthServices._current_login_user("lkadsjlkjaskljdkjaskdjlajldaslkjdak")

    @patch.object(User, "decode_token")
    def test_current_login_user_signature_expired_token(self, mock_decode):
        """ test curren login user but using signature expired token """

        mock_decode.side_effect = SignatureExpiredError(Mock())
        with self.assertRaises(TokenError):
            AuthServices._current_login_user("lkadsjlkjaskljdkjaskdjlajldaslkjdak")

    @patch.object(User, "decode_token")
    def test_current_login_user_invalid_token(self, mock_decode):
        """ test curren login user but using invalid token """

        mock_decode.side_effect = InvalidTokenError(Mock())
        with self.assertRaises(TokenError):
            AuthServices._current_login_user("lkadsjlkjaskljdkjaskdjlajldaslkjdak")

    @patch.object(User, "decode_token")
    def test_current_login_user_empty_payload(self, mock_decode):
        """ test curren login user but using empty payload token"""

        mock_decode.side_effect = EmptyPayloadError
        with self.assertRaises(TokenError):
            AuthServices._current_login_user("lkadsjlkjaskljdkjaskdjlajldaslkjdak")

    def test_create_token_success(self):
        """ test success create access & refresh token"""
        result = AuthServices().create_token({"username" : "MODANAADMIN",\
                                              "password" : "password"})

        self.assertTrue(result["access_token"])
        self.assertTrue(result["refresh_token"])

    def test_create_token_failed_not_found(self):
        """ test failed create access & refresh token because user is not
        created yet"""
        with self.assertRaises(UserNotFoundError):
            result = AuthServices().create_token({"username" : "roserose",\
                                                  "password" : "password"})

    def test_create_token_failed_incorrect_login(self):
        """ test failed create access & refresh token by using invalid
        credentials"""
        with self.assertRaises(InvalidCredentialsError):
            result = AuthServices().create_token({"username" : "MODANAADMIN",\
                                              "password" : "pasword"})

    def test_refresh_token_success(self):
        """ test success refreshing token"""

        user = User.query.filter_by(username="MODANAADMIN").first()
        result = AuthServices().refresh_token(user)

        self.assertTrue(result["access_token"])

    def test_logout_access_token(self):
        """ test blacklist access token """
        result = AuthServices().create_token({"username" : "MODANAADMIN",\
                                              "password" : "password"})

        access_token = result["access_token"]
        result = AuthServices().logout_access_token(access_token)
        self.assertTrue(result[1], 204) # no content

    @patch.object(User, "decode_token")
    def test_logout_access_token_revoked_token(self, mock_decode):
        """ test blacklist access token using revoked token"""
        mock_decode.side_effect = RevokedTokenError

        with self.assertRaises(TokenError):
            result = AuthServices().logout_access_token("123123k123k12;3j12j3j21jj")

    @patch.object(User, "decode_token")
    def test_logout_access_token_signature_expired(self, mock_decode):
        """ test blacklist access token using expired token"""
        mock_decode.side_effect = SignatureExpiredError(Mock())

        with self.assertRaises(TokenError):
            result = AuthServices().logout_access_token("123123k123k12;3j12j3j21jj")

    @patch.object(User, "decode_token")
    def test_logout_access_token_invalid(self, mock_decode):
        """ test blacklist access token using invalid token"""
        mock_decode.side_effect = InvalidTokenError(Mock())

        with self.assertRaises(TokenError):
            result = AuthServices().logout_access_token("123123k123k12;3j12j3j21jj")

    @patch.object(User, "decode_token")
    def test_logout_access_token_empty_payload(self, mock_decode):
        """ test blacklist access token using invalid token"""
        mock_decode.side_effect = EmptyPayloadError

        with self.assertRaises(TokenError):
            result = AuthServices().logout_access_token("123123k123k12;3j12j3j21jj")

    def test_logout_refresh_token(self):
        """ test blacklist access token """
        result = AuthServices().create_token({"username" : "MODANAADMIN",\
                                              "password" : "password"})

        refresh_token = result["refresh_token"]
        result = AuthServices().logout_refresh_token(refresh_token)

        self.assertTrue(result[1], 204) # no content

    @patch.object(User, "decode_token")
    def test_logout_refresh_token_revoked(self, mock_decode):
        """ test blacklist refresh token using revoked token"""
        mock_decode.side_effect = RevokedTokenError

        with self.assertRaises(TokenError):
            result = AuthServices().logout_refresh_token("123123k123k12;3j12j3j21jj")

    @patch.object(User, "decode_token")
    def test_logout_refresh_token_signature_expired(self, mock_decode):
        """ test blacklist refresh token using revoked token"""
        mock_decode.side_effect = SignatureExpiredError(Mock())

        with self.assertRaises(TokenError):
            result = AuthServices().logout_refresh_token("123123k123k12;3j12j3j21jj")

    @patch.object(User, "decode_token")
    def test_logout_refresh_token_invalid_token(self, mock_decode):
        """ test blacklist refresh token using revoked token"""
        mock_decode.side_effect = InvalidTokenError(Mock())

        with self.assertRaises(TokenError):
            result = AuthServices().logout_refresh_token("123123k123k12;3j12j3j21jj")

    @patch.object(User, "decode_token")
    def test_logout_refresh_token_empty_payload(self, mock_decode):
        """ test blacklist refresh token using empty payload """
        mock_decode.side_effect = EmptyPayloadError

        with self.assertRaises(TokenError):
            result = AuthServices().logout_refresh_token("123123k123k12;3j12j3j21jj")
