import functools
from dataclasses import dataclass, asdict
from decimal import Decimal
from enum import Enum
from typing import List, Set, Dict

import boto3
from boto3.dynamodb.conditions import Attr, Key
from botocore.exceptions import ClientError

from common import envs
from common.storage import util
from common.storage.db_util import update_expression


class Entities:
    SESSION = 'SESSION'
    GAME = 'GAME'
    PLAYER = 'PLAYER'
    USER = 'USER'
    QUIZ = 'QUIZ'
    TOPIC = 'TOPIC'
    FACT_SHEET = 'FACT_SHEET'

    @staticmethod
    def player(user_id: str):
        return f'{Entities.PLAYER}#{user_id}'

    @staticmethod
    def quiz(lang: str, eid: str):
        return f'{lang.upper()}#{QuizIds.QUIZ}#{eid}'

    @staticmethod
    def topic(lang: str, eid: str):
        return f'{lang.upper()}#{QuizIds.TOPIC}#{eid}'

    @staticmethod
    def fact_sheet(lang: str, eid: str):
        return f'{lang.upper()}#{QuizIds.FACT_SHEET}#{eid}'


class QuizIds:
    QUIZ = 'QUIZ'
    TOPIC = 'TOPIC'
    FACT_SHEET = 'FACT_SHEET'


@dataclass
class SessionEntity:
    connectionId: str
    sourceIp: str
    connectedAt: str
    entity: str = Entities.SESSION
    active: bool = True
    userId: str = None
    userName: str = None
    ttl: int = util.ttl()


class GameState(str, Enum):
    WAIT_START = "WAIT_START"
    ASK_TOPIC = 'ASK_TOPIC'
    SHOW_TOPIC = 'SHOW_TOPIC'
    ASK_QUESTION = "ASK_QUESTION"
    SHOW_ANSWER = "SHOW_ANSWER"
    SHOW_WINNER = "SHOW_WINNER"


@dataclass
class TopicOption:
    topic: str
    title: str
    image: str = None


@dataclass
class WinnerItem:
    userId: str
    score: Decimal


@dataclass
class Entity:
    # todo implement __post_init__ to initialize dataclass properties
    pass


@dataclass
class GameEntity(Entity):
    gameId: str
    userId: str
    startedAt: str
    entity: str = Entities.GAME
    gameState: GameState = GameState.WAIT_START
    ttl: int = util.ttl()
    question: dict = None
    endedAt: str = None
    taskToken: str = None
    totalNumberOfRounds: int = 3
    totalNumberOfQuestions: int = 5
    roundNo: int = 0
    questionNo: int = 0
    topicOptions: List[TopicOption] = None
    topic: TopicOption = None
    winners: List[WinnerItem] = None
    timerStart: int = None
    timerSeconds: int = None

    def __post_init__(self):
        if self.topicOptions is not None and len(self.topicOptions) > 0 and isinstance(self.topicOptions[0], dict):
            self.topicOptions = [TopicOption(**t) for t in self.topicOptions]
        if self.topic is not None and isinstance(self.topic, dict):
            self.topic = TopicOption(**self.topic)
        if self.winners is not None and len(self.winners) > 0 and isinstance(self.winners[0], dict):
            self.winners = [WinnerItem(**t) for t in self.winners]


@dataclass
class PlayerEntity(Entity):
    gameId: str
    userId: str
    joinedAt: str
    entity: str
    ready: bool = False
    endedAt: str = None
    score: Decimal = Decimal(0.0)
    answer: str = None
    answerTime: int = None
    topicVote: str = None
    ttl: int = util.ttl()


@dataclass
class UserEntity:
    userId: str
    userName: str
    lastActiveAt: str
    avatar: str = "1 13 5 3 0 1 8 4 2 10 3"
    connections: Set[str] = None
    entity: str = Entities.USER
    gameId: str = None
    ttl: int = util.ttl()


class QuizType(str, Enum):
    SELECT_ONE = "SELECT_ONE"
    TYPE_ONE = "TYPE_ONE"
    TYPE_ONE_FROM_SET = "TYPE_ONE_FROM_SET"


@dataclass
class QuizEntity:
    id: str
    entity: str
    quizType: QuizType
    question: str
    title: str
    factSheet: str
    questionColumn: str = None
    questionHintColumn: str = None
    answerColumn: str = None
    answerHintColumn: str = None


@dataclass
class TopicEntity:
    id: str
    entity: str
    title: str
    image: str = None


@dataclass
class FactSheetEntity:
    id: str
    entity: str
    fileKey: str
    columns: List[str] = None
    columnTypes: Dict[str, str] = None

    def column_type(self, column: str):
        return self.columnTypes.get(column, 'string')


@functools.cache
def _dynamodb(_=''):
    print('Dynamodb client created')
    return boto3.resource('dynamodb')


@functools.cache
def _session_table(_=''):
    print('Session client created')
    return _dynamodb().Table(envs.DYNAMODB_SESSION_TABLE_NAME)


@functools.cache
def _game_table(_=''):
    print('Game client created')
    return _dynamodb().Table(envs.DYNAMODB_GAME_TABLE_NAME)


@functools.cache
def _user_table(_=''):
    print('User client created')
    return _dynamodb().Table(envs.DYNAMODB_USER_TABLE_NAME)


@functools.cache
def _quiz_table(_=''):
    print('Quiz client created')
    return _dynamodb().Table(envs.DYNAMODB_QUIZ_TABLE_NAME)


def create_session(connection_id: str, source_ip: str, connected_at: str):
    session = SessionEntity(connection_id, source_ip, connected_at)
    _session_table().put_item(Item=asdict(session))


def delete_session(connection_id: str, user_id=None) -> UserEntity:
    response = _session_table().delete_item(
        Key={'connectionId': connection_id, 'entity': Entities.SESSION},
        ReturnValues='ALL_OLD'
    )
    if not user_id and response.get('Attributes'):
        user_id = response['Attributes']['userId']
    resp = _user_table().update_item(
        Key={'userId': user_id, 'entity': Entities.USER},
        UpdateExpression='DELETE connections :connection',
        ExpressionAttributeValues={
            ':connection': {connection_id}
        },
        ReturnValues='ALL_NEW'
    )
    return UserEntity(**resp['Attributes'])


def get_users(user_ids: List[str]) -> List[UserEntity]:
    return [get_user(user_id) for user_id in user_ids]


def get_user(user_id: str) -> UserEntity:
    response = _user_table().get_item(
        Key={'userId': user_id, 'entity': Entities.USER}
    )
    item = response.get('Item')
    if item:
        return UserEntity(**item)


def update_user(connection_id: str, user_id: str, user_name: str, avatar: str) -> UserEntity:
    _session_table().update_item(
        Key={'connectionId': connection_id, 'entity': Entities.SESSION},
        UpdateExpression='SET userName = :nm, userId = :userId',
        ExpressionAttributeValues={
            ':nm': user_name,
            ':userId': user_id
        },
        ReturnValues='ALL_NEW'
    )
    try:
        resp = _user_table().put_item(
            Item=asdict(UserEntity(user_id, user_name, util.now_iso(), avatar, {connection_id})),
            ConditionExpression=Attr('userId').not_exists(),
            ReturnValues='ALL_OLD'
        )
        return UserEntity(**resp['Attributes'])
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            resp = _user_table().update_item(
                Key={'userId': user_id, 'entity': Entities.USER},
                UpdateExpression='SET userName = :nm, lastActiveAt = :lastActiveAt, avatar = :avatar '
                                 'ADD connections :connection',
                ExpressionAttributeValues={
                    ':nm': user_name,
                    ':avatar': avatar,
                    ':lastActiveAt': util.now_iso(),
                    ':connection': {connection_id}
                },
                ReturnValues='ALL_NEW'
            )
            return UserEntity(**resp['Attributes'])
        else:
            raise e


def create_game(game_id: str, user_id: str):
    game = GameEntity(gameId=game_id, userId=user_id, startedAt=util.now_iso())

    _game_table().put_item(
        Item=asdict(game)
    )


def join_game(game_id: str, user_id: str):
    _user_table().update_item(
        Key={'userId': user_id, 'entity': Entities.USER},
        UpdateExpression='SET gameId = :gameId',
        ExpressionAttributeValues={
            ':gameId': game_id
        }
    )
    player = PlayerEntity(gameId=game_id,
                          userId=user_id,
                          joinedAt=util.now_iso(),
                          entity=Entities.player(user_id))
    try:
        _game_table().put_item(
            Item=asdict(player),
            ConditionExpression=Attr('userId').not_exists(),
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            pass
        else:
            raise e


def get_active_players(game_id: str) -> List[PlayerEntity]:
    response = _game_table().query(
        KeyConditionExpression=Key('gameId').eq(game_id) & Key('entity').begins_with(Entities.PLAYER)
    )

    return [PlayerEntity(**item) for item in response['Items']]


def get_active_player(game_id: str, user_id: str) -> PlayerEntity:
    response = _game_table().get_item(
        Key={'gameId': game_id, 'entity': Entities.player(user_id)}
    )
    item = response.get('Item')
    if item:
        return PlayerEntity(**item)


def get_user_connections(user_ids: List[str]):
    connections = []
    for user_id in user_ids:
        user_entity = get_user(user_id)
        if user_entity.connections:
            connections += user_entity.connections
    return connections


def get_game(game_id: str) -> GameEntity:
    response = _game_table().get_item(
        Key={'gameId': game_id, 'entity': Entities.GAME}
    )
    item = response.get('Item')
    if item:
        return GameEntity(**item)


def get_quizzes(entity_prefix: str) -> List[QuizEntity]:
    response = _quiz_table().query(
        KeyConditionExpression=Key('id').eq(QuizIds.QUIZ) & Key('entity').begins_with(entity_prefix.upper())
    )
    return [QuizEntity(**item) for item in response['Items']]


def get_topics(lang: str) -> List[TopicEntity]:
    response = _quiz_table().query(
        KeyConditionExpression=Key('id').eq(QuizIds.TOPIC) & Key('entity').begins_with(lang.upper())
    )
    return [TopicEntity(**item) for item in response['Items']]


def get_topic(topic: str) -> TopicEntity:
    response = _quiz_table().get_item(
        Key={'id': QuizIds.TOPIC, 'entity': topic}
    )
    item = response.get('Item')
    if item:
        return TopicEntity(**item)


def get_fact_sheet(fact_sheet_id: str) -> FactSheetEntity:
    response = _quiz_table().get_item(
        Key={'id': QuizIds.FACT_SHEET, 'entity': fact_sheet_id}
    )
    item = response.get('Item')
    if item:
        return FactSheetEntity(**item)


def update_game(game_id: str, **kwargs):
    upd_args = update_expression(GameEntity, **kwargs)
    _game_table().update_item(
        Key={'gameId': game_id, 'entity': Entities.GAME},
        **upd_args
    )


def update_player(game_id: str, user_id: str, **kwargs):
    upd_args = update_expression(PlayerEntity, **kwargs)
    _game_table().update_item(
        Key={'gameId': game_id, 'entity': Entities.player(user_id)},
        **upd_args
    )

