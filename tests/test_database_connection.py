import unittest

from tgbot.database import DATABASE


class TestDatabaseConnection(unittest.TestCase):    
    def test_connection(self):
        DATABASE.connect()
        DATABASE.close()
