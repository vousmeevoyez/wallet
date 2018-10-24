import sys
import json
  
sys.path.append("../")
sys.path.append("../app")
sys.path.append("../app/va")

import unittest

from app.va.utility import remote_call

class VAUtilityTest(unittest.TestCase):

    def test_post(self):
        base_url   = "https://apibeta.bni-ecollection.com/"
        secret_key = "8eafc8687722fdd0ef78942309fcd983"
        client_id  = "99099"
        payload    = {}

        result = remote_call.post( base_url, secret_key, client_id, payload )

        expected_result = '{"status":"009","message":"Unexpected Error."}'
        self.assertEqual( result, expected_result)

        payload2 = {'type': 'createbilling', 'client_id': '99099', 'trx_id': 12345, 'trx_amount': 10000, 'billing_type': 'J', 'customer_name': "Kelvin", 'customer_email': '', 'customer_phone': '', 'virtual_account': '', 'datetime_expired': '', 'description': ''}
        result2 = remote_call.post( base_url, secret_key, client_id, payload2 )

        expected_result2 = '{"status":"009","message":"Unexpected Error."}'
        self.assertEqual( result2, expected_result2)

    def test_encrypt(self):
        secret_key = "8eafc8687722fdd0ef78942309fcd983"
        client_id  = "99099"
        paylod     = '{"type" : "createbilling", "client_id" : "99099", "trx_id" : "123000003, "trx_amount" : "10000000", "billing_type" : "z", "customer_name" : "Mr. Marcio Soares", "customer_email" : "marcio@modana.id", "customer_phone" : "08123123123", "virtual_account" : "9889909912345677", "datetime_expired" : "2018-10-10T16:00:00+07:00", "description" : "Payment of Trx 123000001" }'

        result = remote_call.encrypt( client_id, secret_key, paylod)
        self.assertEqual( len(result), 568)

    def test_decrypt(self):
        secret_key = "8eafc8687722fdd0ef78942309fcd983"
        client_id  = "99099"
        token = "HCRRRFFNISMdIR4NZnI/EWIOe0wTEicCSAtVEXh+ZlZOUQoGCApPSxMcED4NAgkGRQwTT1pNSQ0MIwl7PlYrGCUqejxCPE0RZVloSlQDcD8JWD9DEyMfHhMZIk9MRx4RSBMJDBd7UlNgZV5fPkE9VwlxQSEhIhQbHBkicj5JEk0FUwcGC3xfVlBkYFtQez80Iz57EmJODxcMPBQCERBdYFlWEHANfV5URBIQJQtyP2pbTDY9UmRQS1sJRQ50D1dkSApKOns+S2RkZF9PUBF8Ak1/CFxNCw0lDEULDH0PVVFbMQsJen1fUB9QVEcNSzR5CwEUWmVhWlBVSGIHCwJXTQ4RTzp7PiEeIiIjHBRSTk8ccUEcEU4GYVVbZgt9CVFSRlQNDw0HTRERKgdHDVhVTCJXTykhIx8eIBUoVlN5Cx0MTUB1ABBWY1FdVUpQDg0GWwN6TBMSJwJICyRPRFUfIhwVT0pzTR4pISAqEhtKTVQaTk9MExUNRw5NThJ/D1tYYFoNCHI+ESkRQxI7TBgBAlcSP1ZXEkFdWwkjUU9EIiEcIUZ2QTxuCA=="

        expected_result = '{"type" : "createbilling", "client_id" : "99099", "trx_id" : "123000003, "trx_amount" : "10000000", "billing_type" : "z", "customer_name" : "Mr. Marcio Soares", "customer_email" : "marcio@modana.id", "customer_phone" : "08123123123", "virtual_account" : "9889909912345677", "datetime_expired" : "2018-10-10T16:00:00+07:00", "description" : "Payment of Trx 123000001" }'


        result = remote_call.decrypt( client_id, secret_key, token)
        self.assertEqual( result, expected_result)

        token2= ""
        result = remote_call.decrypt( client_id, secret_key, token2)
        self.assertEqual( result, None)

if __name__ == "__main__":
    unittest.main(verbosity=2)

