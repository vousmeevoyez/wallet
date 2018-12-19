import json

from app.test.base  import BaseTestCase

BASE_URL = "/api/v1"
RESOURCE = "/auth/"

class TestAuthRoutes(BaseTestCase):

    def get_access_token(self, username, password):
        return self.client.post(
            BASE_URL + RESOURCE + "token",
            data=dict(
                username=username,
                password=password
            )
        )
    #end def

    def get_refresh_token(self, refresh_token):
        headers = {
            'Authorization': 'Bearer {}'.format(refresh_token)
        }
        return self.client.post(
            BASE_URL + RESOURCE + "refresh",
            headers=headers
        )
    #end def

    def revoke_access_token(self, access_token):
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.post(
            BASE_URL + RESOURCE + "token/revoke",
            headers=headers
        )
    #end def

    def revoke_refresh_token(self, refresh_token):
        headers = {
            'Authorization': 'Bearer {}'.format(refresh_token)
        }
        return self.client.post(
            BASE_URL + RESOURCE + "refresh/revoke",
            headers=headers
        )
    #end def

    def test_get_access_token_success(self):
        result = self.get_access_token("MODANAADMIN", "password")
        response = result.get_json()

        self.assertEqual(result.status_code, 200)
        self.assertTrue(response["data"]["access_token"])
        self.assertTrue(response["data"]["refresh_token"])
    #end def

    def test_get_access_token_failed_record_not_found(self):
        result = self.get_access_token("jennie", "password")
        response = result.get_json()

        self.assertEqual(result.status_code, 404)
    #end def

    def test_get_access_token_failed_invalid_login(self):
        result = self.get_access_token("MODANAADMIN", "pa3sword")
        response = result.get_json()

        self.assertEqual(result.status_code, 400)
    #end def

    def test_get_refresh_token_success(self):
        # login first and get the refersh token
        result = self.get_access_token("MODANAADMIN", "password")
        response = result.get_json()

        refresh_token = response["data"]["refresh_token"]

        result = self.get_refresh_token(refresh_token)
        response = result.get_json()

        self.assertEqual(result.status_code, 200)
    #end def

    def test_get_refresh_token_failed_refresh_token_only(self):
        # login first and get the refersh token
        result = self.get_access_token("MODANAADMIN", "password")
        response = result.get_json()

        access_token = response["data"]["access_token"]

        result = self.get_refresh_token(access_token)
        response = result.get_json()

        self.assertEqual(result.status_code, 405)
    #end def

    def test_get_refresh_token_failed_invalid_token(self):
        refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

        result = self.get_refresh_token(refresh_token)
        response = result.get_json()

        self.assertEqual(result.status_code, 400)
    #end def

    def test_revoke_access_token_success(self):
        # login first and get the refersh token
        result = self.get_access_token("MODANAADMIN", "password")
        response = result.get_json()

        access_token = response["data"]["access_token"]

        result = self.revoke_access_token(access_token)
        response = result.get_json()

        self.assertEqual(result.status_code, 200)
    #end def

    def test_revoke_access_token_failed_invalid_token(self):
        access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

        result = self.revoke_access_token(access_token)
        response = result.get_json()

        self.assertEqual(result.status_code, 400)
    #end def

    def test_revoke_refresh_token_success(self):
        # login first and get the refersh token
        result = self.get_access_token("MODANAADMIN", "password")
        response = result.get_json()

        refresh_token = response["data"]["refresh_token"]

        result = self.revoke_refresh_token(refresh_token)
        response = result.get_json()

        self.assertEqual(result.status_code, 200)
    #end def

    def test_revoke_refresh_token_failed_invalid_token(self):
        refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

        result = self.revoke_refresh_token(refresh_token)
        response = result.get_json()

        self.assertEqual(result.status_code, 400)
    #end def
