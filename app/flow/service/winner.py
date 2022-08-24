import logging

from common.model import ShowWinner
from common.service import broadcast
from common.storage import db
from common.storage.db import GameState, WinnerItem

log = logging.getLogger(__name__)


def show_winner(payload: ShowWinner):
    game_id = payload.gameId

    log.info(f"Determine winners for game {game_id}")
    players = db.get_active_players(game_id)

    players.sort(key=lambda p: p.score, reverse=True)
    max_score = max(p.score for p in players)
    winners = [WinnerItem(p.userId, p.score) for p in players if p.score == max_score]
    log.info(f"Determined winners {winners}")
    db.update_game(game_id,
                   winners=winners,
                   gameState=GameState.SHOW_WINNER)
    log.info(f"Broadcasting results")
    broadcast.send_game_state(game_id)
