""" 
    Test Authentication Services
"""

from app.test.base import BaseTestCase
from app.api.models import User
from app.api.authentication.modules.auth_services import AuthServices

class TestAuthServices(BaseTestCase):
    """ test auth services class"""

    def test_create_access_token(self):
        """ test create access token """
        user = User.query.filter_by(username="jisooo").first()
        result = AuthServices()._create_access_token(user)
        self.assertIsInstance(result, str)

    def test_create_refresh_token(self):
        """ test create refresh token"""
        user = User.query.filter_by(username="jisooo").first()
        result = AuthServices()._create_refresh_token(user)
        self.assertIsInstance(result, str)

    def test_current_login_user(self):
        """ test curren login user"""
        user = User.query.filter_by(username="jisooo").first()
        token = AuthServices()._create_access_token(user)

        result = AuthServices.current_login_user(token)

        self.assertEqual(result["data"]["token_type"], "ACCESS")
        self.assertEqual(result["data"]["user_id"], 2)

    def test_create_token_success(self):
        """ test success create access & refresh token"""
        result = AuthServices().create_token({"username" : "jisooo",\
                                              "password" : "password"})

        self.assertTrue(result["data"]["access_token"])
        self.assertTrue(result["data"]["refresh_token"])

    def test_create_token_failed_not_found(self):
        """ test failed create access & refresh token because user is not
        created yet"""
        result = AuthServices().create_token({"username" : "roserose",\
                                              "password" : "password"})

        self.assertTrue(result[1], 404)

    def test_create_token_failed_incorrect_login(self):
        """ test failed create access & refresh token by using invalid
        credentials"""
        result = AuthServices().create_token({"username" : "jisooo",\
                                              "password" : "passord"})

        self.assertTrue(result[1], 400)

    def test_refresh_token_success(self):
        """ test success refreshing token"""

        user = User.query.filter_by(username="jisooo").first()
        result = AuthServices().refresh_token(user.id)

        self.assertTrue(result["data"]["access_token"])

    def test_refresh_token_failed_not_found(self):
        """ test success refreshing token"""

        result = AuthServices().refresh_token(5)

        self.assertTrue(result[1], 404)

    def test_logout_access_token(self):
        """ test blacklist access token """
        result = AuthServices().create_token({"username" : "jisooo",\
                                              "password" : "password"})

        access_token = result["data"]["access_token"]
        result = AuthServices().logout_access_token(access_token)

        self.assertTrue(result["message"])

    def test_logout_refresh_token(self):
        """ test blacklist access token """
        result = AuthServices().create_token({"username" : "jisooo",\
                                              "password" : "password"})

        refresh_token = result["data"]["refresh_token"]
        result = AuthServices().logout_access_token(refresh_token)

        self.assertTrue(result["message"])
