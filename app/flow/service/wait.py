from common.model import WaitPlayersReady
from common.storage import db


def on_wait_players_ready(payload: WaitPlayersReady):
    db.update_game(payload.gameId, taskToken=payload.taskToken)
