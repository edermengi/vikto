import datetime
import unittest

from storage.db import UserSession


class ConnectTestCase(unittest.TestCase):
    def test_user_session(self):
        session = UserSession('1', '1.2.3.4', datetime.datetime.now().isoformat())
        print(session)
