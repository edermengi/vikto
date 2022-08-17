from common.model import WaitPlayersReady
from common.storage import db


def on_wait_players_ready(payload: WaitPlayersReady):
    db.update_task_token(payload.gameId, payload.taskToken)
