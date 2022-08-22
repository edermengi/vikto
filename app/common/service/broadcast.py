import functools
import json

import boto3

from common import envs
from common.model import GameStateBroadcastPayload, PlayersStateBroadcastPayload


@functools.cache
def _lambda(_=''):
    return boto3.client('lambda')


def send_game_state(game_id: str, user_id: str = None):
    _lambda().invoke_async(
        FunctionName=envs.BROADCAST_LAMBDA_NAME,
        InvokeArgs=json.dumps(GameStateBroadcastPayload(game_id, user_id).asjson())
    )


def send_players_state(game_id: str):
    _lambda().invoke_async(
        FunctionName=envs.BROADCAST_LAMBDA_NAME,
        InvokeArgs=json.dumps(PlayersStateBroadcastPayload(game_id).asjson())
    )
