import secrets
import string

from common.model import NewGameRequest, NewGameResponse, Player
from storage import db


def random_game_id():
    return ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(4))


def new_game(req: NewGameRequest) -> NewGameResponse:
    game_id = random_game_id()
    db.create_game(game_id, req.userId)
    db.join_game(game_id, req.userId)
    player_entities = db.get_active_players(game_id)

    return NewGameResponse(game_id, players=[
        Player(userId=player_entity.userId,
               userName=player_entity.userName)
        for player_entity in player_entities
    ])
