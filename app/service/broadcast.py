import json
from dataclasses import asdict
from typing import List

import boto3

from common import envs
from common.model import WsApiBody

client = boto3.client('apigatewaymanagementapi', endpoint_url=envs.WS_API_GATEWAY_URL)


def send_to_connections(message: WsApiBody, connections: List[str]):
    if not connections:
        return

    data = json.dumps(asdict(message))
    for connection in connections:
        try:
            print(f'Sending to {connection}')
            client.post_to_connection(
                Data=data,
                ConnectionId=connection
            )
        except Exception as e:
            print(e)
