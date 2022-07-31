import datetime
import unittest

from storage.db import UserSessionEntity


class ConnectTestCase(unittest.TestCase):
    def test_user_session(self):
        session = UserSessionEntity('1', '1.2.3.4', datetime.datetime.now().isoformat())
        print(session)
