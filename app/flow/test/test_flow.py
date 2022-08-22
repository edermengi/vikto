import unittest

from common.model import WaitPlayersReady, AskQuestion, ShowAnswer, SfPayload


class FlowTestCase(unittest.TestCase):

    def test_parser(self):
        actual = SfPayload.parse({'event': 'waitPlayersReady', 'gameId': '1', 'taskToken': 'TOKEN'})
        self.assertEqual(WaitPlayersReady('1', 'TOKEN'), actual)

        actual = SfPayload.parse({'event': 'askQuestion', 'gameId': '1', 'taskToken': 'TOKEN'})
        self.assertEqual(AskQuestion('1', 'TOKEN'), actual)
        actual = SfPayload.parse({'event': 'showAnswer', 'gameId': '1'})
        self.assertEqual(ShowAnswer('1'), actual)
