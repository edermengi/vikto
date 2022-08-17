import json
from dataclasses import asdict
from typing import List

import boto3

from common import envs
from common.model import WsApiBody, Actions, GameStateResponse, GameStateBroadcastPayload
from broadcast.mapper import map_player_entities
from common.storage import db
from common.storage.db import UserEntity

client = boto3.client('apigatewaymanagementapi', endpoint_url=envs.WS_API_GATEWAY_URL)


def handler(event, _):
    request = GameStateBroadcastPayload(**event)
    send_game_state(request.gameId)


def send_to_users(message: WsApiBody, user_entities: List[UserEntity]):
    data = json.dumps(asdict(message), default=str)

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
                db.delete_session(connection, user_entity.userId)


def send_game_state(game_id: str):
    players, user_entities = _get_players(game_id)
    game = db.get_game(game_id)
    notification = WsApiBody(
        Actions.GAME_STATE_NOTIFICATION,
        GameStateResponse(
            game_id,
            players,
            game.gameState,
            game.question
        )
    )
    send_to_users(notification, user_entities)


def _get_players(game_id):
    player_entities = db.get_active_players(game_id)
    user_entities = db.get_users([pe.userId for pe in player_entities])
    players = map_player_entities(player_entities, user_entities)
    return players, user_entities
