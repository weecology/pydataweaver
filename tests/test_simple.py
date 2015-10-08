import unittest

import app
import sample


class TestSimple(unittest.TestCase):
    
    def test_failure(self):
        self.assertTrue(False)
        print ("done")
