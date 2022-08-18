from typing import List, Dict

from common.model import Player, Topic, Winner
from common.storage.db import PlayerEntity, UserEntity, TopicOption, WinnerItem


def map_player_entities(player_entities: List[PlayerEntity], user_entities: List[UserEntity]) -> List[Player]:
    users: Dict[str, UserEntity] = {ue.userId: ue for ue in user_entities}
    return [
        Player(
            userId=pe.userId,
            ready=pe.ready,
            score=float(pe.score),
            userName=users.get(pe.userId).userName,
            avatar=users.get(pe.userId).avatar,
            online=len(users.get(pe.userId).connections or {}) > 0
        )
        for pe in player_entities
    ]


def map_winners(winners: List[WinnerItem], user_entities: List[UserEntity]) -> List[Winner]:
    if winners is None:
        return []
    users: Dict[str, UserEntity] = {ue.userId: ue for ue in user_entities}
    return [
        Winner(
            userId=pe.userId,
            score=float(pe.score),
            userName=users.get(pe.userId).userName,
            avatar=users.get(pe.userId).avatar,
        )
        for pe in winners
    ]


def map_topic(topic: TopicOption) -> Topic:
    if topic is not None:
        return Topic(topic.topic, topic.title, topic.image)


def map_topics(topics: List[TopicOption]) -> List[Topic]:
    if topics is not None:
        return [map_topic(t) for t in topics]
