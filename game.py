
"""
game.py

This module contains core game logic, rules, and state transitions.
- Manages game objects, turns, and player actions
- Implements game rules and win/loss conditions
- Provides methods for updating game state
All functions here are focused on the mechanics and rules of gameplay.
"""

from typing import List, Dict, Any, Type, Optional
from map import GameMap
from unit import Unit
from player import Player
from city import City
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
        self.turn: int = turn
        self._next_unit_id: int = 1  # Simple unique ID generator
        # City support
        self.cities: List[City] = []
        # Initialize turn_finished for all players
        self.turn_finished: Dict[str, bool] = {pid: False for pid in self.players}
        # Set current_player to first player if not provided or invalid
        if self.players:
            if current_player in self.players:
                self.current_player = current_player
            else:
                self.current_player = list(self.players.keys())[0]
        else:
            self.current_player = None

    def add_city(self, city: City) -> None:
        self.cities.append(city)

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
                    # Check for at least one passable neighbor
                    neighbors = self.map.neighbors(x, y)
                    if any(self.map.is_tile_passable(n.x, n.y) for n in neighbors):
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

    # --- Turn and round management ---
    def check_and_auto_end_turn(self):
        """
        Automatically end turn for current player if all their units have moved.
        Returns True if turn was ended, False otherwise.
        """
        player_units = [u for u in self.units if u.owner == self.current_player]
        if player_units and all(u.moves == 0 for u in player_units):
            return self.end_turn_for_current_player()
        return False

    def end_turn_for_current_player(self):
        """
        Mark the current player's turn as finished. If all players have finished, advance the round.
        Returns True if round advanced, False otherwise.
        """
        if self.current_player in self.turn_finished:
            self.turn_finished[self.current_player] = True
        # Only advance round if all players have finished
        if all(self.turn_finished.values()):
            self.next_round()
            return True
        # Only rotate to next player if this player has not already finished
        unfinished_players = [pid for pid, finished in self.turn_finished.items() if not finished]
        if unfinished_players:
            # Find next unfinished player
            player_ids = list(self.players.keys())
            idx = player_ids.index(self.current_player)
            for offset in range(1, len(player_ids)):
                next_idx = (idx + offset) % len(player_ids)
                next_pid = player_ids[next_idx]
                if not self.turn_finished[next_pid]:
                    self.current_player = next_pid
                    break
        return False

    def next_round(self):
        """
        Advance to the next round and reset turn_finished for all players.
        """
        self.turn += 1
        # Reset moves for all units
        for unit in self.units:
            unit.reset_moves()
        # Reset turn_finished for all players
        self.turn_finished = {pid: False for pid in self.players}
        # Set current_player to first player
        if self.players:
            self.current_player = list(self.players.keys())[0]

    # Future: add city management, action history, etc.
