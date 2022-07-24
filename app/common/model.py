import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Actions(Enum):
    UPDATE_NAME = '$updateName'
    NEW_GAME = "$newGame"
    READY = "$ready",
    EXIT_GAME = "$exitGame",
    CHOOSE_THEME = "$chooseTheme"


@dataclass
class UpdateNameRequest:
    name: str


@dataclass
class WsApiRequest:
    route_key: str
    source_ip: str
    connection_id: str
    connected_at: str
    body: dict

    @staticmethod
    def parse(event):
        print(event)
        rc = event['requestContext']
        return WsApiRequest(
            route_key=rc['routeKey'],
            source_ip=rc['identity']['sourceIp'],
            connection_id=rc['connectionId'],
            connected_at=datetime.fromtimestamp(rc['connectedAt'] / 1000).isoformat(),
            body=json.loads(event['body']) if event.get('body') else {}
        )

    @property
    def action(self) -> Actions:
        return Actions(self.body['action'])

    @property
    def data(self) -> dict:
        return self.body.get('data')

    @property
    def req_update_name(self) -> UpdateNameRequest:
        return UpdateNameRequest(self.data.get('name'))


@dataclass
class Game:
    GameId: str
    UserId: str
