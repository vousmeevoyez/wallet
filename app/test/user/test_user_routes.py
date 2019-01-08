import json

from unittest.mock import Mock, patch

from app.test.base import BaseTestCase
# mock all response incoming from user services
from app.api.user.modules.user_services import UserServices

BASE_URL = "/api/v1"
RESOURCE = "/users/"

class TestUserRoutes(BaseTestCase):
    """ Test Class for User Routes"""

    def get_access_token(self, username, password):
        """ get access token"""
        return self.client.post(
            BASE_URL + "/auth/" + "token",
            data=dict(
                username=username,
                password=password
            )
        )
    #end def

    def create_user(self, params, access_token):
        """ Create user """
        headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }
        return self.client.post(
            BASE_URL + RESOURCE,
            data=json.dumps({
                "username"     : params["username"],
                "name"         : params["name"],
                "phone_ext"    : params["phone_ext"],
                "phone_number" : params["phone_number"],
                "email"        : params["email"],
                "password"     : params["password"],
                "pin"          : params["pin"],
                "role"         : params["role"],
            }),
            headers=headers
        )
    #end def

    @patch.object(UserServices, "add")
    def test_create_user_routes_success(self, mock_user_services):
        """ test routes function to create user"""
        params = {
            "username"     : "jennie",
            "name"         : "jennie",
            "phone_ext"    : "62",
            "phone_number" : "81219643444",
            "email"        : "jennie@blackpink.com",
            "password"     : "password",
            "pin"          : "123456",
            "role"         : "USER"
        }
        access_token = self.get_access_token("MODANAADMIN", "password")

        mock_user_services.return_value = {""}
        result = self.create_user(params, access_token)
