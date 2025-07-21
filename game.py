from typing import List, Dict, Any, Type, Optional
from map import GameMap
from unit import Unit
from player import Player
# from city import City  # For future expansion
import json

class Game:
    def __init__(self, 
                 game_map: Optional[GameMap] = None, 
                 units: Optional[List[Unit]] = None, 
                 players: Optional[Dict[str, Player]] = None, 
                 current_player: Optional[str] = None, 
                 turn: int = 1):
        self.map: GameMap = game_map if game_map is not None else GameMap()
        self.units: List[Unit] = units if units is not None else []
        self.players: Dict[str, Player] = players if players is not None else {}
        self.current_player: Optional[str] = current_player
        self.turn: int = turn
        self._next_unit_id: int = 1  # Simple unique ID generator
        # Future expansion:
        # self.cities: List[City] = []
        # self.action_history: List[Any] = []

        # --- Initial unit creation logic ---
        if not self.units and self.players:
            # Only add if units not provided and players exist
            first_player_id = list(self.players.keys())[0]
            first_player = self.players[first_player_id]
            # Find two valid, distinct starting tiles
            start_tiles = self._find_starting_tiles(2)
            # Create Settler
            settler = Unit(
                unique_id=self._get_next_unit_id(),
                owner=first_player_id,
                unit_type="settler",
                x=start_tiles[0][0],
                y=start_tiles[0][1]
            )
            self.add_unit(settler)
            first_player.add_unit(settler.unique_id)
            # Create Warrior
            warrior = Unit(
                unique_id=self._get_next_unit_id(),
                owner=first_player_id,
                unit_type="warrior",
                x=start_tiles[1][0],
                y=start_tiles[1][1]
            )
            self.add_unit(warrior)
            first_player.add_unit(warrior.unique_id)

    def _get_next_unit_id(self) -> int:
        uid = self._next_unit_id
        self._next_unit_id += 1
        return uid

    def _find_starting_tiles(self, count: int) -> List[tuple]:
        # Find 'count' distinct, passable tiles for starting units
        found = []
        for x in range(self.map.width):
            for y in range(self.map.height):
                tile = self.map.get_tile(x, y)
                if tile and self.map.is_tile_passable(x, y):
                    if not any((x == fx and y == fy) for fx, fy in found):
                        found.append((x, y))
                        if len(found) == count:
                            return found
        # Fallback: just use (0,0), (1,0) if not enough found
        while len(found) < count:
            found.append((len(found), 0))
        return found

    def to_dict(self) -> Dict[str, Any]:
        return {
            'map': self.map.to_dict(),
            'units': [unit.to_dict() for unit in self.units],
            'players': {name: player.to_dict() for name, player in self.players.items()},
            'current_player': self.current_player,
            'turn': self.turn,
            # 'cities': [city.to_dict() for city in self.cities],
            # 'action_history': self.action_history,
        }

    @classmethod
    def from_dict(cls: Type['Game'], data: Dict[str, Any]) -> 'Game':
        game_map = GameMap.from_dict(data['map'])
        units = [Unit.from_dict(u) for u in data['units']]
        players = {name: Player.from_dict(p) for name, p in data['players'].items()}
        current_player = data.get('current_player')
        turn = data.get('turn', 1)
        # cities = [City.from_dict(c) for c in data.get('cities', [])]
        # action_history = data.get('action_history', [])
        game = cls(game_map, units, players, current_player, turn)
        # game.cities = cities
        # game.action_history = action_history
        return game

    def __repr__(self) -> str:
        return (f"<Game turn={self.turn} current_player={self.current_player} "
                f"units={len(self.units)} players={list(self.players.keys())}>")

    # Helper methods
    def add_unit(self, unit: Unit) -> None:
        self.units.append(unit)

    def remove_unit(self, unit: Unit) -> None:
        self.units = [u for u in self.units if u.unique_id != unit.unique_id]

    def add_player(self, name: str, player: Player) -> None:
        self.players[name] = player

    def next_turn(self) -> None:
        self.turn += 1
        # Rotate current player (simple round-robin)
        if self.players:
            names = list(self.players.keys())
            if self.current_player in names:
                idx = (names.index(self.current_player) + 1) % len(names)
                self.current_player = names[idx]
            else:
                self.current_player = names[0]
        # Reset moves for all units
        for unit in self.units:
            unit.reset_moves()

    # Future: add city management, action history, etc.
