from typing import List

from common.model import Player
from storage.db import PlayerEntity


def map_player_entities(player_entities: List[PlayerEntity]) -> List[Player]:
    return [
        Player(userId=player_entity.userId,
               userName=player_entity.userName)
        for player_entity in player_entities
    ]
