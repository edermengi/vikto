import logging

from common import log
from common.model import WaitPlayersReady, parse_sf_payload, AskQuestion, ShowAnswer
from flow.service import wait, question, answer

logging.basicConfig(level=logging.INFO)

logging.info('Test')


def handler(event, _):
    log.info(f'{event}')
    payload = parse_sf_payload(event)
    if isinstance(payload, WaitPlayersReady):
        wait.on_wait_players_ready(payload)
    elif isinstance(payload, AskQuestion):
        question.ask_question(payload)
    elif isinstance(payload, ShowAnswer):
        answer.show_answer(payload)
    else:
        raise ValueError(f'Unexpected payload: {payload}')
