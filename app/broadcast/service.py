import json
from dataclasses import asdict
from typing import List

import boto3

from broadcast.mapper import map_player_entities, map_topics, map_topic, map_winners
from common import envs
from common.model import WsApiBody, Actions, GameStateResponse, PlayersStateResponse, GameStateBroadcastPayload, \
    PlayersStateBroadcastPayload
from common.storage import db, util
from common.storage.db import UserEntity

client = boto3.client('apigatewaymanagementapi', endpoint_url=envs.WS_API_GATEWAY_URL)


def send_to_users(message: WsApiBody, user_entities: List[UserEntity], game_id: str, user_id: str = None):
    data = json.dumps(asdict(message), default=str)

    for user_entity in user_entities:
        if not user_entity.connections:
            continue
        if not user_entity.gameId == game_id:
            continue
        if user_id and user_entity.userId != user_id:
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


def send_game_state(payload: GameStateBroadcastPayload):
    game_id = payload.gameId
    user_id = payload.userId

    players, user_entities = _get_players(game_id)
    game = db.get_game(game_id)
    notification = WsApiBody(
        Actions.GAME_STATE_NOTIFICATION,
        GameStateResponse(
            game_id,
            players,
            game.gameState,
            game.question,
            topicOptions=map_topics(game.topicOptions),
            topic=map_topic(game.topic),
            winners=map_winners(game.winners, user_entities),
            timerSeconds=util.remaining_seconds(game.timerSeconds, game.timerStart),
            totalNumberOfRounds=game.totalNumberOfRounds,
            totalNumberOfQuestions=game.totalNumberOfQuestions,
            roundNo=game.roundNo,
            questionNo=game.questionNo
        )
    )

    send_to_users(notification, user_entities, game_id, user_id)


def send_players_state(payload: PlayersStateBroadcastPayload):
    game_id = payload.gameId

    players, user_entities = _get_players(game_id)
    notification = WsApiBody(
        Actions.PLAYERS_STATE_NOTIFICATION,
        PlayersStateResponse(
            game_id,
            players
        )
    )
    send_to_users(notification, user_entities, game_id)


def _get_players(game_id):
    player_entities = db.get_active_players(game_id)
    user_entities = db.get_users([pe.userId for pe in player_entities])
    players = map_player_entities(player_entities, user_entities)
    return players, user_entities
