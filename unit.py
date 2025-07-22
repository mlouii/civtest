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

if TYPE_CHECKING:
    from map import GameMap, Tile

class Unit:
    def __init__(self, unique_id: int, owner: str, unit_type: str, x: int, y: int) -> None:
        if unit_type not in UNIT_TYPES:
            raise ValueError(f"Unknown unit_type: {unit_type}")
        self.unique_id: int = unique_id
        self.owner: str = owner
        self.unit_type: str = unit_type
        self.x: int = x
        self.y: int = y
        self.moves: int = UNIT_TYPES[unit_type]["move_points"]
        self.hp: int = UNIT_TYPES[unit_type]["hp"]
        self.selected: bool = False

    def update(self, game_state: "GameMap") -> None:
        # Placeholder for per-turn logic
        pass

    def render(self, surface: any) -> None:
        import pygame
        from config import TILE_SIZE
        from gui_config import PLAYER_COLORS
        config = UNIT_TYPES[self.unit_type]
        px = self.x * TILE_SIZE + TILE_SIZE // 2
        py = self.y * TILE_SIZE + TILE_SIZE // 2

        # Get player color, fallback to gray if not found
        player_color = PLAYER_COLORS.get(self.owner, (128,128,128))

        if self.unit_type == "settler":
            # Flagpole
            pole_height = TILE_SIZE // 2
            pole_width = max(2, TILE_SIZE // 16)
            pole_color = (120, 120, 120)
            flag_color = player_color  # Largest piece: flag
            base_color = player_color
            # Draw pole (vertical line)
            pygame.draw.line(surface, pole_color, (px, py + pole_height//2), (px, py - pole_height//2), pole_width)
            # Draw flag (triangle) at top
            flag_height = TILE_SIZE // 6
            flag_width = TILE_SIZE // 6
            flag_top = (px, py - pole_height//2)
            flag_right = (px + flag_width, py - pole_height//2 + flag_height//2)
            flag_bottom = (px, py - pole_height//2 + flag_height)
            pygame.draw.polygon(surface, flag_color, [flag_top, flag_right, flag_bottom])
            # Draw base (small circle)
            pygame.draw.circle(surface, base_color, (px, py + pole_height//2), pole_width*2)

        elif self.unit_type == "warrior":
            # Shield
            shield_radius = TILE_SIZE // 6
            shield_color = player_color  # Largest piece: shield
            shield_cx = px
            shield_cy = py
            # Draw two crossed spears behind the shield
            spear_color = (200, 200, 50)
            spear_width = max(2, TILE_SIZE // 20)
            spear_length = TILE_SIZE // 2
            # First spear: bottom-left to top-right
            spear1_start = (px - spear_length//2, py + spear_length//2)
            spear1_end = (px + spear_length//2, py - spear_length//2)
            pygame.draw.line(surface, spear_color, spear1_start, spear1_end, spear_width)
            # Second spear: top-left to bottom-right
            spear2_start = (px - spear_length//2, py - spear_length//2)
            spear2_end = (px + spear_length//2, py + spear_length//2)
            pygame.draw.line(surface, spear_color, spear2_start, spear2_end, spear_width)
            # Draw shield centered
            pygame.draw.circle(surface, shield_color, (shield_cx, shield_cy), shield_radius)

        else:
            # Default: draw a circle
            color = player_color  # Largest piece: main circle
            radius = config["radius"]
            pygame.draw.circle(surface, color, (px, py), radius)

        if self.selected:
            pygame.draw.circle(surface, (0,255,255), (px, py), TILE_SIZE//4, 2)

    def move(self, to_x: int, to_y: int, game_map: "GameMap" = None) -> bool:
        if self.can_move(to_x, to_y, game_map):
            self.x = to_x
            self.y = to_y
            self.moves -= 1
            return True
        return False

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

    def to_dict(self) -> dict:
        return {
            "unique_id": self.unique_id,
            "owner": self.owner,
            "unit_type": self.unit_type,
            "x": self.x,
            "y": self.y,
            "moves": self.moves,
            "hp": self.hp,
            "selected": self.selected
        }

    def __repr__(self) -> str:
        return (f"<Unit id={self.unique_id} type={self.unit_type} "
                f"owner={self.owner} pos=({self.x},{self.y}) "
                f"hp={self.hp} moves={self.moves} selected={self.selected}>")

    # Settler ability placeholder
    def found_city(self, game, state):
        if self.unit_type != "settler" or self.owner != game.current_player:
            state.status_msg = DEFAULT_STATUS_MSGS["invalid_move"]
            return False
        tx, ty = self.x, self.y
        tile_occupied = any(c.x == tx and c.y == ty for c in game.cities)
        if tile_occupied or not game.map.is_tile_passable(tx, ty):
            state.status_msg = DEFAULT_STATUS_MSGS["invalid_move"]
            return False
        # Check proximity to other cities

        for city in getattr(game, 'cities', []):
            if abs(city.x - tx) <= MIN_CITY_SPACING and abs(city.y - ty) <= MIN_CITY_SPACING:
                state.status_msg = DEFAULT_STATUS_MSGS["proximity_city"]
                return False
        from city import City
        new_city = City(owner_id=game.current_player, x=tx, y=ty)
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

    # Warrior combat placeholder
    def attack(self, target_unit):
        if self.unit_type == "warrior":
            # Placeholder: implement combat logic
            pass
            # Placeholder: implement combat logic
            pass
