"""
unit.py

This module contains unit data, rendering, and actions.
- Defines unit types, attributes, and movement
- Handles unit rendering and selection
- Manages unit actions and interactions
All functions here are focused on unit logic and visualization.
"""
"""
Unit class for Civ MVP project.
"""

from unit_config import UNIT_TYPES
from gui_config import DEFAULT_STATUS_MSGS
from typing import Optional, TYPE_CHECKING

from config import MIN_CITY_SPACING

from city import City

if TYPE_CHECKING:
    from map import GameMap, Tile

# --- Refactored OOP Unit Hierarchy ---
from abc import ABC, abstractmethod

class Unit(ABC):

    def can_melee_target(self, game_map: "GameMap") -> list:
        """
        Returns a list of adjacent (cardinal) (x, y) tiles that are passable and unoccupied.
        Used to determine which tiles would allow a melee unit to attack this unit.
        """
        attackable_tiles = []
        directions = [(-1,0), (1,0), (0,-1), (0,1)]
        for dx, dy in directions:
            adj_x = self.x + dx
            adj_y = self.y + dy
            if game_map.is_tile_passable(adj_x, adj_y):
                tile = game_map.get_tile(adj_x, adj_y)
                if not hasattr(tile, 'unit') or tile.unit is None:
                    attackable_tiles.append((adj_x, adj_y))
        return attackable_tiles

    def __init__(self, unique_id: int, owner: str, unit_type: str, x: int, y: int, moves: int, selected: bool = False) -> None:
        self.unique_id: int = unique_id
        self.owner: str = owner
        self.unit_type: str = unit_type
        self.x: int = x
        self.y: int = y
        self.moves: int = moves
        self.selected: bool = selected

    def move(self, to_x: int, to_y: int, game_map: "GameMap" = None) -> bool:
        if self.can_move(to_x, to_y, game_map):
            self.x = to_x
            self.y = to_y
            self.moves -= 1
            return True
        return False

    def move_along_path(self, path, game_map=None) -> int:
        """
        Move the unit along the given path (list of (x, y)), using self.move for each step.
        Stops if a move is invalid or out of moves. Returns the number of steps actually moved.
        """
        steps_moved = 0
        for step in path[1:]:  # skip the first step (current position)
            if self.can_move(step[0], step[1], game_map):
                self.move(step[0], step[1], game_map)
                steps_moved += 1
            else:
                break
        return steps_moved

    def can_move(self, to_x: int, to_y: int, game_map: "GameMap") -> bool:
        if self.moves < 1:
            return False
        dx = abs(to_x - self.x)
        dy = abs(to_y - self.y)
        if dx + dy != 1:
            return False
        if game_map and not game_map.is_tile_passable(to_x, to_y):
            return False
        return True

    def reset_moves(self) -> None:
        self.moves = UNIT_TYPES[self.unit_type]["move_points"]
        if hasattr(self, "_attacked_this_turn"):
            self._attacked_this_turn = False

    @abstractmethod
    def render(self, surface: any) -> None:
        pass

    def to_dict(self) -> dict:
        return {
            "unique_id": self.unique_id,
            "owner": self.owner,
            "unit_type": self.unit_type,
            "x": self.x,
            "y": self.y,
            "moves": self.moves,
            "selected": self.selected,
            "class": self.__class__.__name__,
        }

    @staticmethod
    def from_dict(data: dict) -> "Unit":
        unit_type = data["unit_type"]
        if unit_type == "warrior":
            return Warrior.from_dict(data)
        elif unit_type == "settler":
            return Settler.from_dict(data)
        # Add more types as needed
        raise ValueError(f"Unknown unit_type: {unit_type}")

    def __repr__(self) -> str:
        return (f"<{self.__class__.__name__} id={self.unique_id} type={self.unit_type} "
                f"owner={self.owner} pos=({self.x},{self.y}) moves={self.moves} selected={self.selected}>")

class CombatUnit(Unit):
    def __init__(self, unique_id: int, owner: str, unit_type: str, x: int, y: int, moves: int, hp: int, attack: int, selected: bool = False) -> None:
        super().__init__(unique_id, owner, unit_type, x, y, moves, selected)
        self.hp: int = hp
        self.attack: int = attack
        self._attacked_this_turn: bool = False

    def can_attack(self, target_unit: "Unit", game_map: "GameMap") -> bool:
        if self.owner == target_unit.owner:
            return False
        if self.moves < 1:
            return False
        if hasattr(self, "_attacked_this_turn") and self._attacked_this_turn:
            return False
        return True

    def attack_unit(self, target_unit: "Unit", game, game_map: "GameMap") -> bool:
        # General attack logic (no adjacency enforced here)
        if not self.can_attack(target_unit, game_map):
            return False
        if not isinstance(target_unit, Unit):
            return False
        target_unit.take_damage(self.attack, game, game_map, attacker=self)
        self.moves = 0
        self._attacked_this_turn = True
        return True

    def take_damage(self, amount: int, game, game_map: "GameMap", attacker: "Unit" = None) -> None:
        self.hp -= amount
        if self.hp <= 0:
            # Remove from game.units
            if hasattr(game, "units"):
                game.units = [u for u in game.units if u != self]
            if hasattr(game, "players") and self.owner in game.players:
                player = game.players[self.owner]
                if hasattr(player, "units"):
                    player.units = [u for u in player.units if u != self]
            if hasattr(game_map, "get_tile"):
                tile = game_map.get_tile(self.x, self.y)
                if tile and hasattr(tile, "unit") and tile.unit == self:
                    tile.unit = None

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({"hp": self.hp, "attack": self.attack})
        return d

    @staticmethod
    def from_dict(data: dict) -> "CombatUnit":
        # This should not be called directly, use subclass
        raise NotImplementedError

class MeleeUnit(CombatUnit):

    def target_enemy_unit(self, target_unit: "Unit", game, game_map: "GameMap", path_map: dict) -> bool:
        """
        Attempts to move to a valid adjacent tile next to the target_unit (if possible via path_map),
        and attack if possible. If attack is performed, ends this unit's turn (deselects, sets moves to 0).
        Returns True if attack was performed, False otherwise.
        """
        # First, check if already adjacent and can attack
        if self.can_attack(target_unit, game_map):
            attacked = self.attack_unit(target_unit, game, game_map)
            if attacked:
                self.selected = False
                self.moves = 0
                return True
        # Otherwise, try to move to an adjacent tile and attack
        targetable_tiles = target_unit.can_melee_target(game_map)
        for tile in targetable_tiles:
            if tile in path_map and len(path_map[tile]) - 1 <= self.moves:
                self.move_along_path(path_map[tile], game_map)
                if self.can_attack(target_unit, game_map):
                    attacked = self.attack_unit(target_unit, game, game_map)
                    if attacked:
                        self.selected = False
                        self.moves = 0
                        return True
                break
        return False

    def can_attack(self, target_unit: "Unit", game_map: "GameMap") -> bool:
        if not super().can_attack(target_unit, game_map):
            return False
        # Must be adjacent (cardinal directions only)
        dx = abs(self.x - target_unit.x)
        dy = abs(self.y - target_unit.y)
        if dx + dy != 1:
            return False
        return True

    def attack_unit(self, target_unit: "Unit", game, game_map: "GameMap") -> bool:
        # Only attack if adjacent (melee rule)
        dx = abs(self.x - target_unit.x)
        dy = abs(self.y - target_unit.y)
        if dx + dy != 1:
            return False
        return super().attack_unit(target_unit, game, game_map)

class NonCombatUnit(Unit):
    can_be_captured: bool = True

    def take_damage(self, amount: int, game, game_map: "GameMap", attacker: "Unit" = None) -> None:
        # Only allow capture if attacker is a CombatUnit
        self.hp = getattr(self, "hp", UNIT_TYPES[self.unit_type]["hp"]) - amount
        if self.hp <= 0 and attacker is not None and isinstance(attacker, CombatUnit):
            # Capture logic
            old_owner = self.owner
            new_owner = attacker.owner
            self.owner = new_owner
            self.hp = UNIT_TYPES[self.unit_type]["hp"]
            # Remove from old owner's unit list
            if hasattr(game, "players") and old_owner in game.players:
                player = game.players[old_owner]
                if hasattr(player, "units"):
                    player.units = [u for u in player.units if u != self]
            # Add to new owner's unit list
            if hasattr(game, "players") and new_owner in game.players:
                player = game.players[new_owner]
                if hasattr(player, "units") and self not in player.units:
                    player.units.append(self)
            # Ensure unit is in game.units
            if hasattr(game, "units") and self not in game.units:
                game.units.append(self)
            # Place on current tile
            if hasattr(game_map, "get_tile"):
                tile = game_map.get_tile(self.x, self.y)
                if tile is not None:
                    tile.unit = self
            return
        # If not captured, do nothing (non-combat units are not destroyed)

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["hp"] = getattr(self, "hp", UNIT_TYPES[self.unit_type]["hp"])
        return d

    @staticmethod
    def from_dict(data: dict) -> "NonCombatUnit":
        # This should not be called directly, use subclass
        raise NotImplementedError

    def found_city(self, game, state) -> bool:
        if self.unit_type != "settler" or self.owner != game.current_player:
            state.status_msg = DEFAULT_STATUS_MSGS["invalid_move"]
            return False
        tx, ty = self.x, self.y
        tile_occupied = any(c.x == tx and c.y == ty for c in game.cities)
        if tile_occupied or not game.map.is_tile_passable(tx, ty):
            state.status_msg = DEFAULT_STATUS_MSGS["invalid_move"]
            return False
        for city in getattr(game, 'cities', []):
            if abs(city.x - tx) <= MIN_CITY_SPACING and abs(city.y - ty) <= MIN_CITY_SPACING:
                state.status_msg = DEFAULT_STATUS_MSGS["proximity_city"]
                return False
        new_city = City(owner_id=game.current_player, x=tx, y=ty)
        new_city.claim_initial_tiles(game.map, game.cities)
        game.add_city(new_city)
        game.remove_unit(self)
        if game.current_player in game.players:
            player = game.players[game.current_player]
            if hasattr(player, "add_city"):
                player.add_city(new_city)
        state.selected_unit = None
        state.status_msg = DEFAULT_STATUS_MSGS["found_city"]
        state.valid_moves = []
        state.path_map = {}
        return True

# --- Concrete Unit Types ---
class Warrior(MeleeUnit):
    def __init__(self, unique_id: int, owner: str, x: int, y: int, moves: int = None, hp: int = None, attack: int = None, selected: bool = False) -> None:
        ut = UNIT_TYPES["warrior"]
        super().__init__(unique_id, owner, "warrior", x, y, moves if moves is not None else ut["move_points"], hp if hp is not None else ut["hp"], attack if attack is not None else ut["attack"], selected)

    @staticmethod
    def from_dict(data: dict) -> "Warrior":
        return Warrior(
            unique_id=data["unique_id"],
            owner=data["owner"],
            x=data["x"],
            y=data["y"],
            moves=data.get("moves"),
            hp=data.get("hp"),
            attack=data.get("attack"),
            selected=data.get("selected", False)
        )

    def render(self, surface: any) -> None:
        import pygame
        from config import TILE_SIZE
        from gui_config import PLAYER_COLORS
        ut = UNIT_TYPES["warrior"]
        px = self.x * TILE_SIZE + TILE_SIZE // 2
        py = self.y * TILE_SIZE + TILE_SIZE // 2
        player_color = PLAYER_COLORS.get(self.owner, (128,128,128))
        # Shield
        shield_radius = TILE_SIZE // 6
        shield_color = player_color
        shield_cx = px
        shield_cy = py
        # Two crossed spears
        spear_color = (200, 200, 50)
        spear_width = max(2, TILE_SIZE // 20)
        spear_length = TILE_SIZE // 2
        spear1_start = (px - spear_length//2, py + spear_length//2)
        spear1_end = (px + spear_length//2, py - spear_length//2)
        pygame.draw.line(surface, spear_color, spear1_start, spear1_end, spear_width)
        spear2_start = (px - spear_length//2, py - spear_length//2)
        spear2_end = (px + spear_length//2, py + spear_length//2)
        pygame.draw.line(surface, spear_color, spear2_start, spear2_end, spear_width)
        pygame.draw.circle(surface, shield_color, (shield_cx, shield_cy), shield_radius)
        if self.selected:
            pygame.draw.circle(surface, (0,255,255), (px, py), TILE_SIZE//4, 2)

class Settler(NonCombatUnit):
    def __init__(self, unique_id: int, owner: str, x: int, y: int, moves: int = None, hp: int = None, selected: bool = False) -> None:
        ut = UNIT_TYPES["settler"]
        self.hp: int = hp if hp is not None else ut["hp"]
        super().__init__(unique_id, owner, "settler", x, y, moves if moves is not None else ut["move_points"], selected)

    @staticmethod
    def from_dict(data: dict) -> "Settler":
        return Settler(
            unique_id=data["unique_id"],
            owner=data["owner"],
            x=data["x"],
            y=data["y"],
            moves=data.get("moves"),
            hp=data.get("hp"),
            selected=data.get("selected", False)
        )

    def render(self, surface: any) -> None:
        import pygame
        from config import TILE_SIZE
        from gui_config import PLAYER_COLORS
        ut = UNIT_TYPES["settler"]
        px = self.x * TILE_SIZE + TILE_SIZE // 2
        py = self.y * TILE_SIZE + TILE_SIZE // 2
        player_color = PLAYER_COLORS.get(self.owner, (128,128,128))
        pole_height = TILE_SIZE // 2
        pole_width = max(2, TILE_SIZE // 16)
        pole_color = (120, 120, 120)
        flag_color = player_color
        base_color = player_color
        pygame.draw.line(surface, pole_color, (px, py + pole_height//2), (px, py - pole_height//2), pole_width)
        flag_height = TILE_SIZE // 6
        flag_width = TILE_SIZE // 6
        flag_top = (px, py - pole_height//2)
        flag_right = (px + flag_width, py - pole_height//2 + flag_height//2)
        flag_bottom = (px, py - pole_height//2 + flag_height)
        pygame.draw.polygon(surface, flag_color, [flag_top, flag_right, flag_bottom])
        pygame.draw.circle(surface, base_color, (px, py + pole_height//2), pole_width*2)
        if self.selected:
            pygame.draw.circle(surface, (0,255,255), (px, py), TILE_SIZE//4, 2)
