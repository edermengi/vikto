import secrets
import string

from common.model import NewGameRequest, NewGameResponse, JoinGameRequest, JoinGameResponse, ReadyRequest, ReadyResponse
from wsapi.service import broadcast
from common.storage import db


def random_game_id():
    return ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(4))


def new_game(req: NewGameRequest) -> NewGameResponse:
    game_id = random_game_id()
    db.create_game(game_id, req.userId)
    db.join_game(game_id, req.userId)
    broadcast.send_game_state(game_id)

    return NewGameResponse(game_id, False)


def join_game(req: JoinGameRequest) -> JoinGameResponse:
    game_id = req.gameId
    user_id = req.userId

    db.join_game(game_id, user_id)
    broadcast.send_game_state(game_id)

    return JoinGameResponse(game_id, False)


def ready(req: ReadyRequest):
    db.update_ready_status(req.gameId, req.userId)
    broadcast.send_game_state(req.gameId)
    return ReadyResponse()
