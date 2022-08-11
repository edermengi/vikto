from common.model import ConnectRequest, DisconnectRequest, UpdateUserRequest
from service import broadcast
from storage import db


def create_session(req: ConnectRequest):
    db.create_session(req.connection_id, req.source_ip, req.connected_at)


def close_session(req: DisconnectRequest):
    user = db.delete_session(req.connection_id)
    if user.gameId:
        broadcast.send_game_state(user.gameId)


def update_user(req: UpdateUserRequest):
    user = db.update_user(req.connection_id, req.userId, req.userName)
    if user.gameId:
        broadcast.send_game_state(user.gameId)
