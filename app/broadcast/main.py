from broadcast.service import send_game_state, send_players_state
from common import log
from common.model import GameStateBroadcastPayload, BroadcastPayload, \
    PlayersStateBroadcastPayload


def handler(event, _):
    log.info(f'event: {event}')

    request = BroadcastPayload.parse(event)
    if isinstance(request, GameStateBroadcastPayload):
        send_game_state(request)
    elif isinstance(request, PlayersStateBroadcastPayload):
        send_players_state(request)
    else:
        raise ValueError(f'Unexpected request {request}')
