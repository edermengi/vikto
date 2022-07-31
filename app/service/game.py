import uuid

from common.model import NewGameRequest, NewGameResponse
from storage import db


def new_game(req: NewGameRequest) -> NewGameResponse:
    game_id = str(uuid.uuid4())
    db.create_game(game_id, req.userId)
    return NewGameResponse(game_id)
