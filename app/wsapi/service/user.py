from common.model import ConnectRequest, DisconnectRequest, UpdateUserRequest, RegisterUserRequest
from common.service import broadcast
from common.storage import db


def create_session(req: ConnectRequest):
    db.create_session(req.connection_id, req.source_ip, req.connected_at)


def close_session(req: DisconnectRequest):
    user = db.delete_session(req.connection_id)
    if user.gameId:
        broadcast.send_players_state(user.gameId)


def update_user(req: UpdateUserRequest):
    user = db.update_user(req.connection_id, req.userId, req.userName, req.avatar)
    if user.gameId:
        broadcast.send_players_state(user.gameId)


def register_user(req: RegisterUserRequest):
    db.update_user(req.connection_id, req.userId, req.userName, req.avatar)
