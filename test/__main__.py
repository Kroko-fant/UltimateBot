import unittest
from cogs.dawum import *


# Test for Dawum Modul.
# If that failes with a file not found error ensure to have a folder named "data" in your test directory.
class DawumTest(unittest.TestCase):

    def test_illegal_parlaments(self):
        self.assertIsNone(umfrage_ausgeben("-1", 1))
        self.assertIsNone(umfrage_ausgeben("18", 1))
        self.assertIsNone(umfrage_ausgeben("bttttdfsvf", 1))

    def test_valid_codes_single_count(self):
        self.assertTrue(len(umfrage_ausgeben("bt", 1).description) > 20)
        self.assertTrue(len(umfrage_ausgeben("by", 1).description) > 20)
        self.assertTrue(len(umfrage_ausgeben("0", 1).description) > 20)
        self.assertTrue(len(umfrage_ausgeben("1", 1).description) > 20)

    def valid_codes_multi_count(self):
        self.assertTrue(len(umfrage_ausgeben("bt", 35).description) > 20)
        self.assertTrue(len(umfrage_ausgeben("by", 15).description) > 20)
        self.assertTrue(len(umfrage_ausgeben("0", 25).description) > 20)
        self.assertTrue(len(umfrage_ausgeben("1", 45).description) > 20)


if __name__ == '__main__':
    unittest.main()
