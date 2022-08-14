from common.model import parse_ws_request, ConnectRequest, DisconnectRequest, UpdateUserRequest, \
    NewGameRequest, WsApiResponse, ApiResponse, WsApiBody, JoinGameRequest
from wsapi.service import user, game


def handler(event, context):
    print(event)
    req = parse_ws_request(event)
    print(req)
    resp: ApiResponse

    if isinstance(req, ConnectRequest):
        resp = user.create_session(req)
    elif isinstance(req, DisconnectRequest):
        resp = user.close_session(req)
    elif isinstance(req, UpdateUserRequest):
        resp = user.update_user(req)
    elif isinstance(req, NewGameRequest):
        resp = game.new_game(req)
    elif isinstance(req, JoinGameRequest):
        resp = game.join_game(req)
    else:
        raise Exception(f'Not implemented')

    return WsApiResponse(
        statusCode=200,
        body=WsApiBody(action=req.action, data=resp)
    ).json()