import sys

sys.path.append("../")
sys.path.append("../../app")
sys.path.append("../../../")

import unittest
import handler

class HandlerTest(unittest.TestCase):

    def test_test(self):
        self.assertEqual(handler.Handlers().test(), "SUCCESS")

if __name__ == "__main__":
    unittest.main(verbosity=2)
