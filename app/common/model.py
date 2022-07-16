from dataclasses import dataclass
from datetime import datetime


@dataclass
class WsApiRequest:
    route_key: str
    source_ip: str
    connection_id: str
    connected_at: str

    @staticmethod
    def parse(event):
        request_context = event['requestContext']
        return WsApiRequest(
            route_key=request_context['routeKey'],
            source_ip=request_context['identity']['sourceIp'],
            connection_id=request_context['connectionId'],
            connected_at=datetime.fromtimestamp(request_context['connectedAt'] / 1000).isoformat()
        )


@dataclass
class Game:
    GameId: str
    UserId: str
