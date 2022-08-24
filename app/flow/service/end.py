import logging

from common.model import EndGame
from common.storage import db

log = logging.getLogger(__name__)


def end_game(payload: EndGame):
    game_id = payload.gameId

    log.info(f"Cleaning data after game {game_id} ended")
    players = db.get_active_players(game_id)

    for player in players:
        db.update_user(player.userId, gameId=None)
