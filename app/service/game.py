import secrets
import string

from common.model import NewGameRequest, NewGameResponse, JoinGameRequest, JoinGameResponse, \
    WsApiBody, Actions, GameStateResponse
from service import broadcast
from service.mapper import map_player_entities
from storage import db


def random_game_id():
    return ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(4))


def new_game(req: NewGameRequest) -> NewGameResponse:
    game_id = random_game_id()
    db.create_game(game_id, req.userId)
    db.join_game(game_id, req.userId)
    player_entities = db.get_active_players(game_id)

    return NewGameResponse(game_id, players=map_player_entities(player_entities))


def join_game(req: JoinGameRequest) -> JoinGameResponse:
    game_id = req.gameId
    user_id = req.userId

    db.join_game(game_id, user_id)
    player_entities = db.get_active_players(game_id)
    players = map_player_entities(player_entities)

    notification = WsApiBody(Actions.GAME_STATE_NOTIFICATION, GameStateResponse(game_id, players))
    connections = db.get_user_connections([player.userId for player in players])
    broadcast.send_to_connections(notification, connections)

    return JoinGameResponse(game_id, players=players)
