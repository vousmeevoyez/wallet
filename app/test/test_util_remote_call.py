import json
import random
import requests

from unittest.mock import Mock, patch

from app.test.base          import BaseTestCase
from app.api.bank.utility   import remote_call

class TestUtilityRemoteCall(BaseTestCase):

    @patch("requests.post")
    def test_post_success(self, mock_post):
        base_url   = "https://apibeta.bni-ecollection.com/"
        secret_key = "8eafc8687722fdd0ef78942309fcd983"
        client_id  = "99099"
        payload = {'type': 'createbilling', 'client_id': '99099', 'trx_id': "12345", 'trx_amount': "100", 'billing_type': 'j', 'customer_name': "Kelvin", 'customer_email': '', 'customer_phone': '', 'virtual_account': '', 'datetime_expired': '', 'description': ''}

        expected_data = {"virtual_account" : "9889909912345677", "datetime_expired" : "2018-10-10T16:00:00+07:00"}

        encrypted_data = remote_call.encrypt( client_id, secret_key, expected_data)

        mock_post.return_value = Mock()
        mock_post.return_value.json.return_value = { "status" : "0", "data" : encrypted_data }

        result = remote_call.post( base_url, client_id, secret_key, payload )
        self.assertEqual( result["status"], "0")

    def test_encrypt(self):
        secret_key = "8eafc8687722fdd0ef78942309fcd983"
        client_id  = "99099"
        paylod     = '{"type" : "createbilling", "client_id" : "99099", "trx_id" : "123000003, "trx_amount" : "10000000", "billing_type" : "z", "customer_name" : "Mr. Marcio Soares", "customer_email" : "marcio@modana.id", "customer_phone" : "08123123123", "virtual_account" : "9889909912345677", "datetime_expired" : "2018-10-10T16:00:00+07:00", "description" : "Payment of Trx 123000001" }'

        result = remote_call.encrypt( client_id, secret_key, paylod)
        self.assertEqual( len(result), 568)

    def test_decrypt(self):
        secret_key = "8eafc8687722fdd0ef78942309fcd983"
        client_id  = "99099"
        token = "HyRPSlhQISMdIR4NZnI/EWIOe0wTEicCSAtVEXh+ZlZOUQoGCApPSxMcED4NAgkGRQwTT1pNSQ0MIwl7PlYrGCUqejxCPE0RZVloSlQDcD8JWD9DEyMfHhMZIk9MRx4RSBMJDBd7UlNgZV5fPkE9VwlxQSEhIhQbHBkicj5JEk0FUwcGC3xfVlBkYFtQez80Iz57EmJODxcMPBQCERBdYFlWEHANfV5URBIQJQtyP2pbTDY9UmRQS1sJRQ50D1dkSApKOns+S2RkZF9PUBF8Ak1/CFxNCw0lDEULDH0PVVFbMQsJen1fUB9QVEcNSzR5CwEUWmVhWlBVSGIHCwJXTQ4RTzp7PiEeIiIjHBRSTk8ccUEcEU4GYVVbZgt9CVFSRlQNDw0HTRERKgdHDVhVTCJXTykhIx8eIBUoVlN5Cx0MTUB1ABBWY1FdVUpQDg0GWwN6TBMSJwJICyRPRFUfIhwVT0pzTR4pISAqEhtKTVQaTk9MExUNRw5NThJ/D1tYYFoNCHI+ESkRQxI7TBgBAlcSP1ZXEkFdWwkjUU9EIiEcIUZ2QTxuCA=="

        expected_result = '{"type" : "createbilling", "client_id" : "99099", "trx_id" : "123000003, "trx_amount" : "10000000", "billing_type" : "z", "customer_name" : "Mr. Marcio Soares", "customer_email" : "marcio@modana.id", "customer_phone" : "08123123123", "virtual_account" : "9889909912345677", "datetime_expired" : "2018-10-10T16:00:00+07:00", "description" : "Payment of Trx 123000001" }'

        result = remote_call.decrypt( client_id, secret_key, token)
        self.assertEqual( result, None)


if __name__ == "__main__":
    unittest.main(verbosity=2)

