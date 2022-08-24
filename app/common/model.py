import json
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import List, ClassVar, Type


class Actions(str, Enum):
    CONNECT = '$connect'
    DISCONNECT = '$disconnect'
    REGISTER_USER = '$registerUser'
    UPDATE_USER = '$updateUser'
    NEW_GAME = "$newGame"
    JOIN_GAME = "$joinGame"
    READY = "$ready",
    ANSWER = "$answer"
    CHOOSE_TOPIC = "$chooseTopic"
    EXIT_GAME = "$exitGame",
    CHOOSE_THEME = "$chooseTheme"
    GAME_STATE_NOTIFICATION = "$gamePush"
    PLAYERS_STATE_NOTIFICATION = "$playersPush"


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
class RegisterUserRequest(WsApiRequest):
    userId: str
    userName: str
    avatar: str


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


@dataclass
class ReadyRequest(WsApiRequest):
    userId: str
    gameId: str


@dataclass
class AnswerRequest(WsApiRequest):
    userId: str
    gameId: str
    answer: str


@dataclass
class ChooseTopicRequest(WsApiRequest):
    userId: str
    gameId: str
    topic: str


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
    ready: bool
    topicVote: str
    answered: bool
    score: float = 0.0


@dataclass
class NewGameResponse(ApiResponse):
    gameId: str


@dataclass
class JoinGameResponse(NewGameResponse):
    pass


@dataclass
class ReadyResponse(ApiResponse):
    pass


@dataclass
class AnswerResponse(ApiResponse):
    pass


@dataclass
class AnswerOption:
    answer: str
    hint: str
    right: bool = False


@dataclass
class Question:
    title: str
    question: str
    questionItem: str
    questionHint: str
    answerOptions: List[AnswerOption]


@dataclass
class Topic:
    topic: str
    title: str
    image: str = None


@dataclass
class Winner:
    userId: str
    userName: str
    avatar: str
    score: float


@dataclass
class GameStateResponse(ApiResponse):
    gameId: str
    players: List[Player]
    gameState: str = None
    question: dict = None
    topicOptions: List[Topic] = None
    topic: Topic = None
    winners: List[Winner] = None
    timerSeconds: int = None
    totalNumberOfRounds: int = None
    totalNumberOfQuestions: int = None
    roundNo: int = None
    questionNo: int = None
    # question: Question = None


@dataclass
class PlayersStateResponse(ApiResponse):
    gameId: str
    players: List[Player]


@dataclass
class BroadcastPayload:
    event: ClassVar[str]

    @staticmethod
    def parse(payload: dict):
        return parse_payload(BroadcastPayload, 'event', payload)

    def asjson(self):
        return {'event': self.event, **asdict(self)}


@dataclass
class GameStateBroadcastPayload(BroadcastPayload):
    event: ClassVar[str] = "broadcastGame"
    gameId: str
    userId: str = None


@dataclass
class PlayersStateBroadcastPayload(BroadcastPayload):
    event: ClassVar[str] = "broadcastPlayers"
    gameId: str


@dataclass
class GameStepFunctionInput:
    gameId: str


@dataclass
class SfPayload:
    event: ClassVar[str]

    @staticmethod
    def parse(payload: dict):
        return parse_payload(SfPayload, 'event', payload)


@dataclass
class WaitPlayersReady(SfPayload):
    event: ClassVar[str] = "waitPlayersReady"
    gameId: str
    taskToken: str


@dataclass
class AskTopic(SfPayload):
    event: ClassVar[str] = "askTopic"
    gameId: str
    taskToken: str


@dataclass
class AskQuestion(SfPayload):
    event: ClassVar[str] = "askQuestion"
    gameId: str
    taskToken: str


@dataclass
class ShowAnswer(SfPayload):
    event: ClassVar[str] = "showAnswer"
    gameId: str


@dataclass
class ShowTopic(SfPayload):
    event: ClassVar[str] = "showTopic"
    gameId: str


@dataclass
class ShowWinner(SfPayload):
    event: ClassVar[str] = "showWinner"
    gameId: str


@dataclass
class EndGame(SfPayload):
    event: ClassVar[str] = "endGame"
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
        if req.action == Actions.REGISTER_USER:
            return RegisterUserRequest(**asdict(req), **req.data)
        if req.action == Actions.UPDATE_USER:
            return UpdateUserRequest(**asdict(req), **req.data)
        elif req.action == Actions.NEW_GAME:
            return NewGameRequest(**asdict(req), **req.data)
        elif req.action == Actions.JOIN_GAME:
            return JoinGameRequest(**asdict(req), **req.data)
        elif req.action == Actions.READY:
            return ReadyRequest(**asdict(req), **req.data)
        elif req.action == Actions.ANSWER:
            return AnswerRequest(**asdict(req), **req.data)
        elif req.action == Actions.CHOOSE_TOPIC:
            return ChooseTopicRequest(**asdict(req), **req.data)
    else:
        raise Exception(f'Unexpected route {req.route_key} and action {req.action}')


def parse_payload(cls: Type, type_field: str, payload: dict):
    event = payload.get(type_field)
    if event is None:
        raise ValueError(f'Unable to parse payload. There is no {type_field} property in {payload}')

    for payload_cls in cls.__subclasses__():
        if getattr(payload_cls, type_field) == event:
            return payload_cls(**{k: payload[k] for k in payload if k != type_field})

    raise ValueError(f'Unable to parse payload. There is no corresponding class for [{event}]')
