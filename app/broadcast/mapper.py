from typing import List, Dict

from common.model import Player
from common.storage.db import PlayerEntity, UserEntity


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
