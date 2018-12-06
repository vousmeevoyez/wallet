import unittest
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
        return self.client.post(
            BASE_URL + RESOURCE + "refresh",
            headers=refresh_token
        )
    #end def

    def revoke_access_token(self, access_token):
        return self.client.post(
            BASE_URL + RESOURCE + "token/revoke",
            headers=access_token
        )
    #end def

    def revoke_refresh_token(self, refresh_token):
        return self.client.post(
            BASE_URL + RESOURCE + "refresh/revoke",
            headers=refresh_token
        )
    #end def

    def test_get_access_token(self):
        pass

