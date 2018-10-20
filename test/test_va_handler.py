import sys
import json
  
sys.path.append("../")
sys.path.append("../app")
sys.path.append("../app/va")

import unittest

from app.va import handler

class VAHandlerTest(unittest.TestCase):

    def test_create_va(self):
        result = handler.Handlers().create_va(12345, 10000, "Kelvin")
        expected_result = '{"status":"002","message":"IP address not allowed or wrong Client ID."}'
        self.assertEqual( result, expected_result)

if __name__ == "__main__":
    unittest.main(verbosity=2)

