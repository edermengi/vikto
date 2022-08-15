import unittest

from common.model import WaitPlayersReady, parse_sf_payload


class FlowTestCase(unittest.TestCase):

    def test_payload_parser(self):
        actual = parse_sf_payload({'event': 'waitPlayersReady', 'gameId': '1', 'taskToken': 'TOKEN'})
        self.assertEqual(WaitPlayersReady('1', 'TOKEN'), actual)
