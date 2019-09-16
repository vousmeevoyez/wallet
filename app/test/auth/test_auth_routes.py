""" 
    Test Authentication Routes
"""
from unittest.mock import Mock, patch

from app.test.base import BaseTestCase

from app.api.auth.modules.auth_services import AuthServices


class TestAuthRoutes(BaseTestCase):
    """ Test Auth Routes Class"""

    def setUp(self):
        super().setUp()

    def test_get_access_token_success(self):
        """ test success get access token"""
        result = self.get_access_token("MODANAADMIN", "password")
        response = result.get_json()

        self.assertEqual(result.status_code, 200)
        self.assertTrue(response["data"]["access_token"])
        self.assertTrue(response["data"]["refresh_token"])

    # end def

    def test_get_access_token_failed_record_not_found(self):
        """ test failed record not found get access token"""
        result = self.get_access_token("jennie", "password")
        response = result.get_json()
        # print(response)
        self.assertEqual(result.status_code, 404)

    # end def

    def test_get_access_token_failed_invalid_login(self):
        """ tes invalid login get access token"""
        result = self.get_access_token("MODANAADMIN", "pa3sword")
        response = result.get_json()
        # print(response)
        self.assertEqual(result.status_code, 401)

    # end def

    def test_get_refresh_token_success(self):
        """ tes success get refresh token"""
        # login first and get the refersh token
        result = self.get_access_token("MODANAADMIN", "password")
        response = result.get_json()

        refresh_token = response["data"]["refresh_token"]

        result = self.get_refresh_token(refresh_token)
        response = result.get_json()

        self.assertEqual(result.status_code, 200)

    # end def

    def test_get_refresh_token_failed_refresh_token_only(self):
        """ tes failed get refresh token"""
        # login first and get the refersh token
        result = self.get_access_token("MODANAADMIN", "password")
        response = result.get_json()

        access_token = response["data"]["access_token"]

        result = self.get_refresh_token(access_token)
        response = result.get_json()

        self.assertEqual(result.status_code, 405)

    # end def

    def test_get_refresh_token_failed_invalid_token(self):
        """ test get refresh token using invalid token"""
        refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

        result = self.get_refresh_token(refresh_token)
        self.assertEqual(result.status_code, 401)

    # end def

    def test_revoke_token_success(self):
        """ test revoking access token"""
        # login first and get the refersh token
        result = self.get_access_token("MODANAADMIN", "password")
        response = result.get_json()

        access_token = response["data"]["access_token"]

        result = self.revoke_token(access_token)
        self.assertEqual(result.status_code, 204)

    # end def

    def test_revoke_token_failed_invalid_token(self):
        """ test failed revoking access token using invalid token"""
        access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

        result = self.revoke_token(access_token)
        self.assertEqual(result.status_code, 401)

    # end def
