from dataclasses import dataclass, asdict
from typing import List

import boto3
from boto3.dynamodb.conditions import Attr, Key
from botocore.exceptions import ClientError

from common import envs
from storage import util


class Entities:
    SESSION = 'SESSION'
    GAME = 'GAME'
    PLAYER = 'PLAYER'
    USER = 'USER'


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


@dataclass
class PlayerEntity:
    gameId: str
    userId: str
    userName: str
    joinedAt: str
    entity: str
    endedAt: str = None
    ttl: int = util.ttl()


@dataclass
class UserEntity:
    userId: str
    userName: str
    lastActiveAt: str
    entity: str = Entities.USER
    gameId: str = None
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


def _user_table(user_table=None):
    if not user_table:
        user_table = _dynamodb().Table(envs.DYNAMODB_USER_TABLE_NAME)
    return user_table


def create_session(connection_id: str, source_ip: str, connected_at: str):
    session = UserSessionEntity(connection_id, source_ip, connected_at)
    _session_table().put_item(Item=asdict(session))


def delete_session(connection_id: str):
    _session_table().delete_item(
        Key={'connectionId': connection_id, 'entity': Entities.SESSION}
    )


def get_user(user_id: str) -> UserEntity:
    response = _user_table().get_item(
        Key={'userId': user_id, 'entity': Entities.USER}
    )
    return UserEntity(**response['Item'])


def update_user(connection_id: str, user_id: str, user_name: str):
    _session_table().update_item(
        Key={'connectionId': connection_id, 'entity': Entities.SESSION},
        UpdateExpression='set userName = :nm, userId = :userId',
        ExpressionAttributeValues={
            ':nm': user_name,
            ':userId': user_id
        }
    )
    try:
        _user_table().put_item(
            Item=asdict(UserEntity(user_id, user_name, util.now_iso())),
            ConditionExpression=Attr('userId').not_exists()
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            _user_table().update_item(
                Key={'userId': user_id, 'entity': Entities.USER},
                UpdateExpression='set userName = :nm, lastActiveAt = :lastActiveAt',
                ExpressionAttributeValues={
                    ':nm': user_name,
                    ':lastActiveAt': util.now_iso()
                }
            )


def create_game(game_id: str, user_id: str):
    game = GameEntity(gameId=game_id, userId=user_id, startedAt=util.now_iso())

    _game_table().put_item(
        Item=asdict(game)
    )


def join_game(game_id: str, user_id: str):
    user = get_user(user_id)
    player = PlayerEntity(gameId=game_id,
                          userId=user_id,
                          userName=user.userName,
                          joinedAt=util.now_iso(),
                          entity=f'{Entities.PLAYER}#{user_id}')

    _game_table().put_item(
        Item=asdict(player)
    )


def get_active_players(game_id: str) -> List[PlayerEntity]:
    response = _game_table().query(
        KeyConditionExpression=Key('gameId').eq(game_id) & Key('entity').begins_with(Entities.PLAYER)
    )

    return [PlayerEntity(**item) for item in response['Items']]
