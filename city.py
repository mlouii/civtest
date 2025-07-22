"""
city.py

This module contains city data, rendering, and management.
- Defines city attributes and population
- Handles city rendering and selection
- Manages city growth and production
All functions here are focused on city logic and visualization.
"""
from typing import Dict, Any, Type, Optional
import uuid
import random
import pygame
from config import TILE_SIZE

CITY_NAME_POOL = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
    "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"
]

class City:
    def __init__(
        self,
        owner_id: str,
        x: int,
        y: int,
        name: Optional[str] = None,
        city_id: Optional[str] = None,
        population: int = 5,
        worked_tiles: Optional[list] = None
    ) -> None:
        self.city_id: str = city_id if city_id is not None else str(uuid.uuid4())
        self.owner_id: str = owner_id
        self.x: int = x
        self.y: int = y
        self.population: int = population
        if name is not None:
            self.name: str = name
        else:
            self.name: str = random.choice(CITY_NAME_POOL)
        # Worked tiles: list of (x, y) tuples
        if worked_tiles is not None:
            self.worked_tiles = worked_tiles
        else:
            self.worked_tiles = [(self.x, self.y)]  # Start with city center only

    def claim_center_tile(self, game_map):
        tile = game_map.get_tile(self.x, self.y)
        if tile:
            tile.claim(self.city_id, self.owner_id)


    def claim_initial_tiles(self, game_map, all_cities, radius=1):
        # Ensure this city is included in all_cities
        if self not in all_cities:
            all_cities = all_cities + [self]
        # Always claim center tile
        self.claim_center_tile(game_map)
        self.update_worked_tiles(game_map, all_cities, radius)

    def get_potential_worked_tiles(self, game_map, all_cities, radius=1) -> list:
        # Returns valid candidate tiles for expansion
        candidates = []
        for dx in range(-radius, radius+1):
            for dy in range(-radius, radius+1):
                tx, ty = self.x + dx, self.y + dy
                if (tx, ty) in self.worked_tiles:
                    continue
                tile = game_map.get_tile(tx, ty)
                if not tile:
                    continue
                # Must not be water or mountain
                if getattr(tile, 'terrain', None) in ('water', 'mountain'):
                    continue
                # Must not be worked by another city
                if any((tx, ty) in c.worked_tiles for c in all_cities if c != self):
                    continue
                # Must be adjacent to city or another worked tile
                if self.is_adjacent_to_worked(tx, ty):
                    candidates.append((tx, ty))
        return candidates

    def is_adjacent_to_worked(self, tx, ty) -> bool:
        # Checks if (tx, ty) is adjacent to any worked tile
        for wx, wy in self.worked_tiles:
            if abs(wx - tx) <= 1 and abs(wy - ty) <= 1 and (wx != tx or wy != ty):
                return True
        return False

    def expand_worked_tiles(self, game_map, all_cities, radius=1):
        # Add tiles up to population, keeping contiguity
        while len(self.worked_tiles) < self.population:
            candidates = self.get_potential_worked_tiles(game_map, all_cities, radius)
            if not candidates:
                break
            # Pick nearest candidate to city center
            candidates.sort(key=lambda t: abs(t[0]-self.x)+abs(t[1]-self.y))
            chosen = candidates[0]
            self.worked_tiles.append(chosen)
            tile = game_map.get_tile(*chosen)
            if tile:
                tile.claim(self.city_id, self.owner_id)
                print(f"City {self.name} claimed tile {chosen} at ({self.x}, {self.y})")

    def contract_worked_tiles(self, game_map=None):
        # Remove last-added worked tile if population decreased
        while len(self.worked_tiles) > self.population:
            removed = self.worked_tiles.pop()
            if game_map:
                tile = game_map.get_tile(*removed)
                if tile and tile.city_id == self.city_id:
                    tile.release()

    def update_worked_tiles(self, game_map, all_cities, radius=1):
        # Call after population change
        self.expand_worked_tiles(game_map, all_cities, radius)
        self.contract_worked_tiles(game_map)

    def release_all_worked_tiles(self, game_map):
        for tx, ty in self.worked_tiles:
            tile = game_map.get_tile(tx, ty)
            if tile and tile.city_id == self.city_id:
                tile.release()
        self.worked_tiles = []

    def is_tile_worked(self, tx, ty) -> bool:
        return (tx, ty) in self.worked_tiles

    def worked_tile_claim(self, tx, ty) -> bool:
        # Returns True if this city claims the tile
        return (tx, ty) in self.worked_tiles

    def render(self, surface: Any, owner_color: Any = (0, 0, 0), selected: bool = False, font: Any = None) -> None:
        px = self.x * TILE_SIZE + TILE_SIZE // 2
        py = self.y * TILE_SIZE + TILE_SIZE // 2
        radius = TILE_SIZE // 3
        # Draw city icon (filled circle)
        pygame.draw.circle(surface, owner_color, (px, py), radius)
        # Draw border in black
        pygame.draw.circle(surface, (0, 0, 0), (px, py), radius, 2)
        # Draw city name below icon
        if font is None:
            font = pygame.font.SysFont(None, 22)
        name_surf = font.render(self.name, True, (0, 0, 0))
        name_rect = name_surf.get_rect(center=(px, py + radius + 12))
        surface.blit(name_surf, name_rect)
        # Highlight if selected
        if selected:
            pygame.draw.circle(surface, (0,255,255), (px, py), radius+6, 2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "city_id": self.city_id,
            "owner_id": self.owner_id,
            "name": self.name,
            "population": self.population,
            "x": self.x,
            "y": self.y,
            "worked_tiles": self.worked_tiles
        }

    @classmethod
    def from_dict(cls: Type['City'], data: Dict[str, Any]) -> 'City':
        return cls(
            owner_id=data["owner_id"],
            x=data["x"],
            y=data["y"],
            name=data.get("name"),
            city_id=data.get("city_id"),
            population=data.get("population", 1),
            worked_tiles=data.get("worked_tiles", [(data["x"], data["y"])])
        )

    def __repr__(self) -> str:
        return (f"<City id={self.city_id} name={self.name} owner={self.owner_id} "
                f"pos=({self.x},{self.y}) pop={self.population}>")
