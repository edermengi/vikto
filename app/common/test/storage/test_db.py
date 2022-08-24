import unittest
from dataclasses import asdict

from common.storage.db import PlayerEntity, TopicOption, GameEntity, UserEntity
from common.storage.db_util import update_expression, Add, Del


class DbTestCase(unittest.TestCase):

    def test_player_entity(self):
        player = asdict(PlayerEntity("GameID", "UserID", "", "PLAYER#UserID"))
        self.assertEqual("PLAYER#UserID", player['entity'])

    def test_update_expression_game_entity(self):
        actual = update_expression(
            GameEntity,
            question=None,
            topicOptions=[TopicOption('topic', 'title', 'image')],
            roundNo=Add(1)
        )
        expected = {
            'UpdateExpression': 'SET #question = :question, #topicOptions = :topicOptions ADD #roundNo :roundNo',
            'ExpressionAttributeValues': {
                ':question': None,
                ':roundNo': 1,
                ':topicOptions': [
                    {'topic': 'topic', 'title': 'title', 'image': 'image'}
                ]},
            'ExpressionAttributeNames': {
                '#question': 'question',
                '#topicOptions': 'topicOptions',
                '#roundNo': 'roundNo'
            }
        }
        self.assertEqual(expected, actual)

    def test_update_expression_user_entity(self):
        actual = update_expression(
            UserEntity,
            connections=Del({'connection'})
        )
        expected = {
            'UpdateExpression': 'DELETE #connections :connections',
            'ExpressionAttributeValues': {
                ':connections': {'connection'}
            },
            'ExpressionAttributeNames': {
                '#connections': 'connections'
            }
        }
        self.assertEqual(expected, actual)
