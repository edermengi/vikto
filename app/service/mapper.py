from typing import List, Dict

from common.model import Player
from storage.db import PlayerEntity, UserEntity


def map_player_entities(player_entities: List[PlayerEntity], user_entities: List[UserEntity]) -> List[Player]:
    users: Dict[str, UserEntity] = {ue.userId: ue for ue in user_entities}

    return [
        Player(
            userId=pe.userId,
            userName=pe.userName,
            online=len(users.get(pe.userId).connections or {}) > 0
        )
        for pe in player_entities
    ]
