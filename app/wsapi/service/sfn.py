import datetime
import json
from dataclasses import asdict

import boto3

from common import envs
from common.model import GameStepFunctionInput

client = boto3.client('stepfunctions')


def start(game_id: str):
    exec_name = game_id + "-" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    message = json.dumps(asdict(GameStepFunctionInput(game_id)))

    client.start_execution(
        stateMachineArn=envs.GAME_SFN_ARN,
        name=exec_name,
        input=message
    )


def send_task_success(task_token: str):
    client.send_task_success(
        taskToken=task_token,
        output='{}'
    )
