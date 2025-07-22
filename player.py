"""
player.py

This module contains player data, actions, and state.
- Defines player attributes and resources
- Manages player actions and turn logic
- Tracks player progress and status
All functions here are focused on player management and interaction.
"""
from typing import List, Dict, Any, Type, Optional, Tuple

class Player:
    def is_out_of_moves(self, game) -> bool:
        # Returns True if all units owned by this player are out of moves
        for unit in game.units:
            if unit.owner == self.player_id and unit.moves > 0:
                return False
        return True
    def __init__(self, player_id: str, is_human: bool = True, color: Optional[Any] = None):
        self.player_id: str = player_id
        self.is_human: bool = is_human
        self.unit_ids: List[int] = []
        self.city_ids: List[int] = []
        self.resources: Dict[str, int] = {"food": 0, "prod": 0, "gold": 0}
        self.color: Optional[Any] = color

    def to_dict(self) -> Dict[str, Any]:
        return {
            "player_id": self.player_id,
            "is_human": self.is_human,
            "unit_ids": self.unit_ids,
            "city_ids": self.city_ids,
            "resources": self.resources,
            "color": self.color,
        }

    @classmethod
    def from_dict(cls: Type["Player"], data: Dict[str, Any]) -> "Player":
        player = cls(
            player_id=data["player_id"],
            is_human=data.get("is_human", True),
            color=data.get("color")
        )
        player.unit_ids = data.get("unit_ids", [])
        player.city_ids = data.get("city_ids", [])
        player.resources = data.get("resources", {"food": 0, "prod": 0, "gold": 0})
        return player

    def __repr__(self) -> str:
        return (f"<Player id={self.player_id} human={self.is_human} "
                f"units={self.unit_ids} cities={self.city_ids} resources={self.resources}>")

    def add_unit(self, unit_id: int) -> None:
        if unit_id not in self.unit_ids:
            self.unit_ids.append(unit_id)

    def remove_unit(self, unit_id: int) -> None:
        if unit_id in self.unit_ids:
            self.unit_ids.remove(unit_id)

    def add_city(self, city_id: int) -> None:
        if city_id not in self.city_ids:
            self.city_ids.append(city_id)

    def remove_city(self, city_id: int) -> None:
        if city_id in self.city_ids:
            self.city_ids.remove(city_id)
