from common.model import WaitPlayersReady, parse_sf_payload
from flow.service import game


def handler(event, _):
    payload = parse_sf_payload(event)
    print(payload)
    if isinstance(payload, WaitPlayersReady):
        game.on_wait_players_ready(payload)
    else:
        raise ValueError(f'Unexpected payload: {payload}')
