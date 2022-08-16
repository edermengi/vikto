import unittest

from common.model import WaitPlayersReady, parse_sf_payload, AskQuestion, ShowAnswer


class FlowTestCase(unittest.TestCase):

    def test_parser(self):
        actual = parse_sf_payload({'event': 'waitPlayersReady', 'gameId': '1', 'taskToken': 'TOKEN'})
        self.assertEqual(WaitPlayersReady('1', 'TOKEN'), actual)

        actual = parse_sf_payload({'event': 'askQuestion', 'gameId': '1', 'taskToken': 'TOKEN'})
        self.assertEqual(AskQuestion('1', 'TOKEN'), actual)
        actual = parse_sf_payload({'event': 'showAnswer', 'gameId': '1'})
        self.assertEqual(ShowAnswer('1'), actual)
