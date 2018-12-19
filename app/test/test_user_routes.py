import json
from unittest.mock import Mock, patch

from app.test.base          import BaseTestCase
from app.api.models         import User, VirtualAccount, Wallet
from app.api.bank.utility   import remote_call

BASE_URL = "/api/v1"
RESOURCE = "/auth/"

class TestUserRoutes(BaseTestCase):

    def setUp(self):
        self.mock_post_patcher = patch("remote_call.post")
        self.mock_post = self.mock_post_patcher.start()

    def tearDown(self):
        self.mock_post_patcher.stop()

    """
        HELPER
    """

    def _create_user(self, username, name, phone_ext, phone_number, email, password, pin, role):
        return self.client.post(
            BASE_URL + RESOURCE + "users",
            data=json.dumps({
                "username"     : username,
                "name"         : name,
                "phone_ext"    : phone_ext,
                "phone_number" : phone_number,
                "email"        : email,
                "password"     : password,
                "pin"          : pin,
                "role"         : role,
            })
        )

    """
        USER
    """
    def test_register_user_success(self):
        expected_value = {
            "status" : "000",
            "message" : {'trx_id': "123", 'virtual_account': "122222" }
        }

        # MOCK RESPONSE
        self.mock_post.return_value = Mock()
        self.mock_post.return_value.json.return_value  = expected_value

        result = self._create_user("Jennie", "jennie", "62", "81219644324", "jennie@blackpink.com", "password", "123456", "1")
        response = result.get_json()
        print(response)

        self.assertEqual(response["status_code"], 0)
        self.assertTrue(response["data"]["user_id"])
        self.assertTrue(response["data"]["wallet_id"])

        # check database entry make sure data inserted correctly
        user = User.query.all()
        self.assertEqual(len(user), 1)

        wallet = Wallet.query.all()
        self.assertEqual(len(wallet), 1)

        va = VirtualAccount.query.all()
        self.assertEqual(len(va), 1)
    #end def

if __name__ == "__main__":
    unittest.main(verbosity=2)
