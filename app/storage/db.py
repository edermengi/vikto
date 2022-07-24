import datetime
from dataclasses import dataclass, asdict

import boto3

from common import envs


class Entities:
    SESSION = 'SESSION'


@dataclass
class UserSession:
    connectionId: str
    sourceIp: str
    connectedAt: str
    entity: str = Entities.SESSION
    active: bool = True
    userName: str = None


def _dynamodb(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
    return dynamodb


def _session_table(session_table=None):
    if not session_table:
        session_table = _dynamodb().Table(envs.DYNAMODB_SESSION_TABLE_NAME)
    return session_table


def create_session(connection_id: str, source_ip: str, connected_at: str):
    session = UserSession(connection_id, source_ip, connected_at)
    _session_table().put_item(Item=asdict(session))


def close_session(connection_id: str):
    _session_table().update_item(
        Key={'connectionId': connection_id, 'entity': Entities.SESSION},
        UpdateExpression='set active = :active, disconnectedAt = :disconnectedAt',
        ExpressionAttributeValues={
            ':active': False,
            ':disconnectedAt': datetime.datetime.now().isoformat()
        }
    )


def update_name(connection_id: str, name: str):
    _session_table().update_item(
        Key={'connectionId': connection_id, 'entity': Entities.SESSION},
        UpdateExpression='set userName = :nm',
        ExpressionAttributeValues={
            ':nm': name
        }
    )
