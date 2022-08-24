from common.model import ConnectRequest, DisconnectRequest, UpdateUserRequest, RegisterUserRequest
from common.service import broadcast
from common.storage import db, util
from common.storage.db_util import Add, Del


def create_session(req: ConnectRequest):
    db.create_session(req.connection_id, req.source_ip, req.connected_at)


def close_session(req: DisconnectRequest):
    session = db.get_session(req.connection_id)
    if session:
        db.delete_session(req.connection_id)
        db.update_user(session.userId,
                       connections=Del({req.connection_id}))
        user = db.get_user(session.userId)
        if user.gameId:
            broadcast.send_players_state(user.gameId)


def update_user(req: UpdateUserRequest):
    db.update_user(req.userId,
                   userName=req.userName,
                   avatar=req.avatar)
    user = db.get_user(req.userId)
    if user.gameId:
        broadcast.send_players_state(user.gameId)


def register_user(req: RegisterUserRequest):
    db.update_session(req.connection_id,
                      userId=req.userId,
                      userName=req.userName)
    db.update_user(req.userId,
                   connections=Add({req.connection_id}),
                   userName=req.userName,
                   avatar=req.avatar,
                   ttl=util.now_timestamp(),
                   lastActiveAt=util.now_iso())
