import logging
from random import Random
from typing import List

from common.model import AskTopic, ShowTopic
from common.service import broadcast
from common.storage import db, util
from common.storage.db import TopicOption, GameState
from common.storage.db_util import Add

log = logging.getLogger(__name__)

# How many topics to select from
OPTION_TOPICS_SIZE = 6

WAIT_SECONDS = 30


def ask_topic(payload: AskTopic):
    game_id = payload.gameId

    all_topics = db.get_topics('RU')
    log.info(f'Found {len(all_topics)} topics')
    topics = Random().sample(all_topics, OPTION_TOPICS_SIZE)

    topic_options = [TopicOption(topic=t.entity, title=t.title, image=t.image) for t in topics]
    log.info(f'Randomly picked topics {topic_options}')
    db.update_game(game_id,
                   topicOptions=topic_options,
                   gameState=GameState.ASK_TOPIC,
                   taskToken=payload.taskToken,
                   roundNo=Add(1),
                   questionNo=0,
                   timerStart=util.now_timestamp(),
                   timerSeconds=WAIT_SECONDS)
    log.info(f'Broadcast ask topic state')
    broadcast.send_game_state(game_id)


def _determine_winner_topic(topics: List[str], topic_options: List[TopicOption]) -> TopicOption:
    topic = Random().choice(topics)
    for topic_option in topic_options:
        if topic_option.topic == topic:
            return topic_option
    log.warning('Topic winner selection logic is broken. Select topic randomly')
    return Random().choice(topic_options)


def show_topic(payload: ShowTopic):
    game_id = payload.gameId

    game = db.get_game(game_id)
    log.info(f'Determine topic winner for game {game_id}')
    players = db.get_active_players(game_id)
    topics = [p.topicVote for p in players if p.topicVote]
    if len(topics) == 0:
        topics = [t.topic for t in game.topicOptions]
    topic = _determine_winner_topic(topics, game.topicOptions)

    log.info(f'Clean topic votes')
    for player in players:
        db.update_player_topic_vote(game_id, player.userId, '')

    log.info(f'Update game state and topic winner {topic}')
    db.update_game(game_id,
                   topic=topic,
                   gameState=GameState.SHOW_TOPIC,
                   topicOptions=None)
    log.info(f'Broadcast show topic state')
    broadcast.send_game_state(game_id)
