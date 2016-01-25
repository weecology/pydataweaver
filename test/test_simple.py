import unittest
import os

import sqlalchemy


class TestDB(unittest.TestCase):
    def setUp(self):
        url = os.getenv("DB_TEST_URL")
        if not url:
            self.skipTest("No database URL set")
        self.engine = sqlalchemy.create_engine(url)