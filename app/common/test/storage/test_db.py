import unittest
from dataclasses import asdict

from common.storage.db import PlayerEntity


class DbTestCase(unittest.TestCase):

    def test_player_entity(self):
        player = asdict(PlayerEntity("GameID", "UserID", "", "PLAYER#UserID"))
        self.assertEqual("PLAYER#UserID", player['entity'])
