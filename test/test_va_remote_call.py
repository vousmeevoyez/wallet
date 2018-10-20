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
        print(result2)

        expected_result2 = '{"status":"009","message":"Unexpected Error."}'
        self.assertEqual( result2, expected_result2)

if __name__ == "__main__":
    unittest.main(verbosity=2)

