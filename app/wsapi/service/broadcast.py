import json
from dataclasses import asdict

import boto3

from common import envs
from common.model import GameStateBroadcastPayload

lambda_client = boto3.client('lambda')


def send_game_state(game_id: str):
    lambda_client.invoke_async(
        FunctionName=envs.BROADCAST_LAMBDA_NAME,
        InvokeArgs=json.dumps(asdict(GameStateBroadcastPayload(game_id)))
    )
