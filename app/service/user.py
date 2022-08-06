from common.model import ConnectRequest, DisconnectRequest, UpdateUserRequest
from storage import db


def create_session(req: ConnectRequest):
    db.create_session(req.connection_id, req.source_ip, req.connected_at)


def close_session(req: DisconnectRequest):
    db.delete_session(req.connection_id)


def update_user(req: UpdateUserRequest):
    db.update_user(req.connection_id, req.userId, req.userName)
