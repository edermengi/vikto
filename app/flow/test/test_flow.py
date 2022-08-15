import unittest

from common.model import StartGamePayload, parse_sf_payload


class FlowTestCase(unittest.TestCase):

    def test_payload_parser(self):
        actual = parse_sf_payload({'event': 'startGame', 'gameId': '1', 'taskToken': 'TOKEN'})
        self.assertEqual(StartGamePayload('1', 'TOKEN'), actual)
