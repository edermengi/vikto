import secrets
import string

from common.model import NewGameRequest, NewGameResponse
from storage import db


def random_game_id():
    return ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(4))


def new_game(req: NewGameRequest) -> NewGameResponse:
    game_id = random_game_id()
    db.create_game(game_id, req.userId)
    return NewGameResponse(game_id)
