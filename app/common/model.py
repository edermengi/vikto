import json
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import List


class Actions(str, Enum):
    CONNECT = '$connect'
    DISCONNECT = '$disconnect'
    UPDATE_USER = '$updateUser'
    NEW_GAME = "$newGame"
    JOIN_GAME = "$joinGame"
    READY = "$ready",
    EXIT_GAME = "$exitGame",
    CHOOSE_THEME = "$chooseTheme"
    GAME_STATE_NOTIFICATION = "$gameStateNotification"


@dataclass
class WsApiRequest:
    route_key: str
    source_ip: str
    connection_id: str
    connected_at: str
    body: dict

    @property
    def action(self) -> Actions:
        return Actions(self.body['action'] if self.body else self.route_key)

    @property
    def data(self) -> dict:
        return self.body.get('data')


@dataclass
class ConnectRequest(WsApiRequest):
    pass


@dataclass
class DisconnectRequest(WsApiRequest):
    pass


@dataclass
class UpdateUserRequest(WsApiRequest):
    userId: str
    userName: str
    avatar: str


@dataclass
class NewGameRequest(WsApiRequest):
    userId: str


@dataclass
class JoinGameRequest(WsApiRequest):
    userId: str
    gameId: str


@dataclass()
class ApiResponse:
    pass


@dataclass
class WsApiBody:
    action: Actions
    data: ApiResponse


@dataclass
class WsApiResponse:
    statusCode: int
    body: WsApiBody

    def json(self):
        return {
            'statusCode': self.statusCode,
            'body': json.dumps(asdict(self.body))
        }


@dataclass
class Player:
    userId: str
    userName: str
    avatar: str
    online: bool
    score: float = 0.0


@dataclass
class NewGameResponse(ApiResponse):
    gameId: str


@dataclass
class JoinGameResponse(NewGameResponse):
    pass


@dataclass()
class GameStateResponse(ApiResponse):
    gameId: str
    players: List[Player]


@dataclass
class GameStateBroadcastPayload:
    gameId: str


class ApiError(Exception):
    def __init__(self, message: str):
        self.message = message


def parse_ws_request(event):
    print(event)
    rc = event['requestContext']
    req = WsApiRequest(
        route_key=rc['routeKey'],
        source_ip=rc['identity']['sourceIp'],
        connection_id=rc['connectionId'],
        connected_at=datetime.fromtimestamp(rc['connectedAt'] / 1000).isoformat(),
        body=json.loads(event['body']) if event.get('body') else {}
    )
    if req.route_key == '$connect':
        return ConnectRequest(**asdict(req))
    elif req.route_key == '$disconnect':
        return DisconnectRequest(**asdict(req))
    elif req.route_key == '$default':
        if req.action == Actions.UPDATE_USER:
            return UpdateUserRequest(**asdict(req), **req.data)
        elif req.action == Actions.NEW_GAME:
            return NewGameRequest(**asdict(req), **req.data)
        elif req.action == Actions.JOIN_GAME:
            return JoinGameRequest(**asdict(req), **req.data)
    else:
        raise Exception(f'Unexpected route {req.route_key} and action {req.action}')
