import logging

from common import log
from common.model import WaitPlayersReady, parse_sf_payload, AskQuestion
from flow.service import game

logging.basicConfig(level=logging.INFO)

logging.info('Test')


def handler(event, _):
    payload = parse_sf_payload(event)
    log.info(f'{payload}')
    if isinstance(payload, WaitPlayersReady):
        game.on_wait_players_ready(payload)
    elif isinstance(payload, AskQuestion):
        game.ask_question(payload)
    else:
        raise ValueError(f'Unexpected payload: {payload}')
