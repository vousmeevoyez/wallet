import json

from unittest.mock import Mock, patch

from app.test.base import BaseTestCase

BASE_URL = "/api/v1"
RESOURCE = "/users/"

class TestUserRoutes(BaseTestCase):

    def get_access_token(self, username, password):
        return self.client.post(
            BASE_URL + "/auth/" + "token",
            data=dict(
                username=username,
                password=password
            )
        )
    #end def

    def create_user(self, params):
        return self.client.post(
            BASE_URL + RESOURCE + "token",
            data=json.dumps({
                "username"     : params["username"],
                "name"         : params["name"],
                "phone_ext"    : params["phone_ext"],
                "phone_number" : params["phone_number"],
                "email"        : params["email"],
                "password"     : params["password"],
                "pin"          : params["pin"],
                "role"         : params["role"],
            })
        )
    #end def
