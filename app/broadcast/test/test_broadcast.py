import unittest

from common.model import BroadcastPayload, \
    GameStateBroadcastPayload, PlayersStateBroadcastPayload


class BroadcastTestCase(unittest.TestCase):

    def test_parser(self):
        actual = BroadcastPayload.parse({'event': 'broadcastGame', 'gameId': '1'})
        self.assertEqual(GameStateBroadcastPayload('1'), actual)

        actual = BroadcastPayload.parse({'event': 'broadcastPlayers', 'gameId': '1'})
        self.assertEqual(PlayersStateBroadcastPayload('1'), actual)

    def test_json_serializer(self):
        actual = GameStateBroadcastPayload('1').asjson()
        self.assertEqual(actual, {'event': 'broadcastGame', 'gameId': '1', 'userId': None})

        actual = PlayersStateBroadcastPayload('1').asjson()
        self.assertEqual(actual, {'event': 'broadcastPlayers', 'gameId': '1'})
