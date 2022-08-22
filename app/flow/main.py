import logging

from common import log
from common.model import WaitPlayersReady, AskQuestion, ShowAnswer, AskTopic, ShowTopic, ShowWinner, SfPayload
from flow.service import wait, question, answer, topic, winner

logging.basicConfig(level=logging.INFO)

logging.info('Test')


def handler(event, _):
    log.info(f'{event}')
    payload = SfPayload.parse(event)
    if isinstance(payload, WaitPlayersReady):
        response = wait.on_wait_players_ready(payload)
    elif isinstance(payload, AskTopic):
        response = topic.ask_topic(payload)
    elif isinstance(payload, ShowTopic):
        response = topic.show_topic(payload)
    elif isinstance(payload, AskQuestion):
        response = question.ask_question(payload)
    elif isinstance(payload, ShowAnswer):
        response = answer.show_answer(payload)
    elif isinstance(payload, ShowWinner):
        response = winner.show_winner(payload)
    else:
        raise ValueError(f'Unexpected payload: {payload}')
    return response
