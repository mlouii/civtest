"""
map.py

This module contains map data, rendering, and tile logic.
- Defines the game map grid and tile properties
- Handles map rendering and updates
- Provides utility functions for tile access and manipulation
All functions here are focused on map structure and visualization.
"""
# map.py
# This module generates a tile-based map similar to Civilization games.
# It creates a grid of tiles, assigns terrain types, and clusters biomes.

import random
import pygame
from typing import List, Optional, Tuple, Any
from config import (
    MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, BASE_WATER_RATIO,
    LAND_SMOOTH_PASSES, FOREST_RATIO, HILL_RATIO, MOUNTAIN_RATIO, PLAINS_RATIO, SEED,
    TERRAIN_TYPES
)

class Tile:
    # Represents a single tile on the map
    def __init__(self, x: int, y: int, terrain: str) -> None:
        self.x: int = x
        self.y: int = y
        self.terrain: str = terrain
        self.city: Optional[Any] = None
        self.unit: Optional[Any] = None

    @property
    def color(self) -> Tuple[int, int, int]:
        # Returns the color for rendering based on terrain type
        return TERRAIN_TYPES[self.terrain]["color"]

    def update(self, game_state: Any) -> None:
        # Placeholder for future tile updates (e.g., city/unit logic)
        pass

    def render(self, surface: Any) -> None:
        # Draws the tile on the given surface using pygame
        pygame.draw.rect(
            surface,
            self.color,
            (self.x * TILE_SIZE, self.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        )
        pygame.draw.rect(
            surface,
            (50, 50, 50),
            (self.x * TILE_SIZE, self.y * TILE_SIZE, TILE_SIZE, TILE_SIZE),
            1
        )

class GameMap:
    # Generates and manages the entire map grid
    def __init__(
        self, width: int, height: int,
        override_water: Optional[float] = None, override_forest: Optional[float] = None,
        override_hill: Optional[float] = None, override_mountain: Optional[float] = None,
        override_plains: Optional[float] = None, override_smoothing: Optional[int] = None
    ) -> None:
        # Set random seed for reproducibility
        if SEED is not None:
            random.seed(SEED)
        self.width: int = width
        self.height: int = height

        # Use overrides or config values for terrain ratios and smoothing
        base_water = override_water if override_water is not None else BASE_WATER_RATIO
        forest = override_forest if override_forest is not None else FOREST_RATIO
        hill = override_hill if override_hill is not None else HILL_RATIO
        mountain = override_mountain if override_mountain is not None else MOUNTAIN_RATIO
        plains = override_plains if override_plains is not None else PLAINS_RATIO
        smoothing = override_smoothing if override_smoothing is not None else LAND_SMOOTH_PASSES

        # 1. Initial random land/water assignment
        grid: List[List[int]] = [[0 if random.random() > base_water else 1 for _ in range(width)] for _ in range(height)]

        # 2. Smooth land/water using cellular automata
        for _ in range(int(smoothing)):
            grid = self._smooth(grid)

        # 3. Ensure a minimum amount of water tiles
        total_water = sum(grid[y][x] for y in range(height) for x in range(width))
        min_water = int(base_water * width * height * 0.8)
        tries = 0
        while total_water < min_water and tries < 500:
            x = random.randint(0, width-1)
            y = random.randint(0, height-1)
            if grid[y][x] == 0:
                grid[y][x] = 1
                total_water += 1
            tries += 1

        # 4. Create Tile objects for each grid cell
        self.tiles: List[List[Tile]] = []
        for y in range(height):
            row = []
            for x in range(width):
                terrain = "water" if grid[y][x] == 1 else "grassland"
                row.append(Tile(x, y, terrain))
            self.tiles.append(row)

        # 5. Add land biomes (forest, hill, mountain, plains) as clusters on land tiles
        self._add_land_biomes("forest", forest)
        self._add_land_biomes("hill", hill)
        self._add_land_biomes("mountain", mountain)
        self._add_land_biomes("plains", plains)

    def _smooth(self, grid: List[List[int]]) -> List[List[int]]:
        # Applies cellular automata smoothing to the land/water grid
        new_grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        for y in range(self.height):
            for x in range(self.width):
                water_neighbors = 0
                for dx in [-1,0,1]:
                    for dy in [-1,0,1]:
                        nx, ny = x+dx, y+dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            if grid[ny][nx] == 1:
                                water_neighbors += 1
                # If more than 3 neighbors are water, make this tile water
                if water_neighbors > 3:
                    new_grid[y][x] = 1
                else:
                    new_grid[y][x] = 0
        return new_grid

    def _add_land_biomes(self, terrain: str, ratio: float) -> None:
        # Adds clusters of a specific terrain type to grassland tiles
        total_land = sum(1 for row in self.tiles for tile in row if tile.terrain == "grassland")
        n_tiles = int(ratio * total_land)
        tries = 0
        max_tries = n_tiles * 8
        while n_tiles > 0 and tries < max_tries:
            tries += 1
            y = random.randint(0, self.height - 1)
            x = random.randint(0, self.width - 1)
            tile = self.tiles[y][x]
            if tile.terrain != "grassland":
                continue
            cluster_size = random.randint(1, 5)
            for _ in range(cluster_size):
                dx, dy = random.randint(-1, 1), random.randint(-1, 1)
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    ntile = self.tiles[ny][nx]
                    if ntile.terrain == "grassland":
                        ntile.terrain = terrain
                        n_tiles -= 1
                        if n_tiles <= 0:
                            break

    def update(self, game_state: Any) -> None:
        # Updates all tiles (placeholder for future logic)
        for row in self.tiles:
            for tile in row:
                tile.update(game_state)

    def render(self, surface: Any, game: Optional[Any] = None) -> None:
        # Renders all tiles to the given surface
        for row in self.tiles:
            for tile in row:
                tile.render(surface)
        # Render all units if a Game object is provided
        if game is not None and hasattr(game, "units"):
            for unit in game.units:
                unit.render(surface)

    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        # Returns the tile at (x, y) or None if out of bounds
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None

    def neighbors(self, x: int, y: int) -> List[Tile]:
        # Returns the cardinal (N, S, E, W) neighbors of a tile
        dirs = [(-1,0), (1,0), (0,-1), (0,1)]
        return [self.get_tile(x+dx, y+dy)
                for dx,dy in dirs if self.get_tile(x+dx, y+dy)]

    def is_tile_passable(self, x: int, y: int) -> bool:
        tile = self.get_tile(x, y)
        if tile is None:
            return False
        # Example: only water is impassable
        return tile.terrain != "water"

    def __repr__(self) -> str:
        # String representation for debugging
        return f"<GameMap {self.width}x{self.height}>"
