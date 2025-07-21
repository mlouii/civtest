# map.py

import random
from config import (
    MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, BASE_WATER_RATIO,
    LAND_SMOOTH_PASSES, FOREST_RATIO, HILL_RATIO, MOUNTAIN_RATIO, PLAINS_RATIO, SEED
)

TERRAIN_TYPES = {
    "grassland": {"color": (50, 200, 50), "food": 2, "prod": 1},
    "plains":    {"color": (200, 200, 100), "food": 1, "prod": 2},
    "forest":    {"color": (34, 139, 34),   "food": 1, "prod": 2},
    "hill":      {"color": (139, 69, 19),   "food": 1, "prod": 2},
    "mountain":  {"color": (110, 110, 110), "food": 0, "prod": 0},
    "water":     {"color": (65, 105, 225),  "food": 1, "prod": 0},
}

class Tile:
    def __init__(self, x, y, terrain):
        self.x = x
        self.y = y
        self.terrain = terrain
        self.city = None
        self.unit = None

    @property
    def color(self):
        return TERRAIN_TYPES[self.terrain]["color"]

    def update(self, game_state):
        pass

    def render(self, surface):
        import pygame
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
    def __init__(
        self, width, height,
        override_water=None, override_forest=None, override_hill=None,
        override_mountain=None, override_plains=None, override_smoothing=None
    ):
        from config import (
            BASE_WATER_RATIO, FOREST_RATIO, HILL_RATIO, MOUNTAIN_RATIO, PLAINS_RATIO, LAND_SMOOTH_PASSES, SEED
        )
        if SEED is not None:
            random.seed(SEED)
        self.width = width
        self.height = height

        base_water = override_water if override_water is not None else BASE_WATER_RATIO
        forest = override_forest if override_forest is not None else FOREST_RATIO
        hill = override_hill if override_hill is not None else HILL_RATIO
        mountain = override_mountain if override_mountain is not None else MOUNTAIN_RATIO
        plains = override_plains if override_plains is not None else PLAINS_RATIO
        smoothing = override_smoothing if override_smoothing is not None else LAND_SMOOTH_PASSES

        # 1. Initial random land/water
        grid = [[0 if random.random() > base_water else 1 for _ in range(width)] for _ in range(height)]

        # 2. Smooth with cellular automata
        for _ in range(int(smoothing)):
            grid = self._smooth(grid)

        # 3. Guarantee minimum water
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

        # 4. Create tile objects
        self.tiles = []
        for y in range(height):
            row = []
            for x in range(width):
                terrain = "water" if grid[y][x] == 1 else "grassland"
                row.append(Tile(x, y, terrain))
            self.tiles.append(row)

        # 5. Add land biomes as clusters, only on land
        self._add_land_biomes("forest", forest)
        self._add_land_biomes("hill", hill)
        self._add_land_biomes("mountain", mountain)
        self._add_land_biomes("plains", plains)

    def _smooth(self, grid):
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
                if water_neighbors > 4:
                    new_grid[y][x] = 1
                else:
                    new_grid[y][x] = 0
        return new_grid

    def _add_land_biomes(self, terrain, ratio):
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

    def update(self, game_state):
        for row in self.tiles:
            for tile in row:
                tile.update(game_state)

    def render(self, surface):
        for row in self.tiles:
            for tile in row:
                tile.render(surface)

    def get_tile(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None

    def neighbors(self, x, y):
        dirs = [(-1,0), (1,0), (0,-1), (0,1)]
        return [self.get_tile(x+dx, y+dy)
                for dx,dy in dirs if self.get_tile(x+dx, y+dy)]

    def __repr__(self):
        return f"<GameMap {self.width}x{self.height}>"
