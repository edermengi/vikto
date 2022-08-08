import json
from dataclasses import asdict
from typing import List

import boto3

from common import envs
from common.model import WsApiBody
from storage.db import UserEntity

client = boto3.client('apigatewaymanagementapi', endpoint_url=envs.WS_API_GATEWAY_URL)


def send_to_users(message: WsApiBody, user_entities: List[UserEntity]):
    data = json.dumps(asdict(message))

    for user_entity in user_entities:
        if not user_entity.connections:
            continue
        for connection in user_entity.connections:
            try:
                print(f'Sending to {connection}')
                client.post_to_connection(
                    Data=data,
                    ConnectionId=connection
                )
            except Exception as e:
                print(e)
