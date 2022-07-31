import datetime
from dataclasses import dataclass, asdict

import boto3

from common import envs
from storage import util


class Entities:
    SESSION = 'SESSION'
    GAME = 'GAME'


@dataclass
class UserSessionEntity:
    connectionId: str
    sourceIp: str
    connectedAt: str
    entity: str = Entities.SESSION
    active: bool = True
    userName: str = None
    ttl: int = util.ttl()


@dataclass
class GameEntity:
    gameId: str
    userId: str
    startedAt: str
    entity: str = Entities.GAME
    endedAt: str = None
    ttl: int = util.ttl()


def _dynamodb(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
    return dynamodb


def _session_table(session_table=None):
    if not session_table:
        session_table = _dynamodb().Table(envs.DYNAMODB_SESSION_TABLE_NAME)
    return session_table


def _game_table(game_table=None):
    if not game_table:
        game_table = _dynamodb().Table(envs.DYNAMODB_GAME_TABLE_NAME)
    return game_table


def create_session(connection_id: str, source_ip: str, connected_at: str):
    session = UserSessionEntity(connection_id, source_ip, connected_at)
    _session_table().put_item(Item=asdict(session))


def close_session(connection_id: str):
    _session_table().update_item(
        Key={'connectionId': connection_id, 'entity': Entities.SESSION},
        UpdateExpression='set active = :active, disconnectedAt = :disconnectedAt',
        ExpressionAttributeValues={
            ':active': False,
            ':disconnectedAt': util.now_iso()
        }
    )


def update_user(connection_id: str, user_id: str, user_name: str):
    _session_table().update_item(
        Key={'connectionId': connection_id, 'entity': Entities.SESSION},
        UpdateExpression='set userName = :nm, userId = :userId',
        ExpressionAttributeValues={
            ':nm': user_name,
            ':userId': user_id
        }
    )


def create_game(game_id: str, user_id: str):
    game = GameEntity(gameId=game_id, userId=user_id, startedAt=util.now_iso())

    _game_table().put_item(
        Item=asdict(game)
    )
