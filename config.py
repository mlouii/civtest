
"""
config.py

This module contains game configuration constants and settings.
- Defines map size, tile size, and other game parameters
- Centralizes configuration for easy tuning
All variables here are focused on game setup and configuration.
"""
# Map dimensions (number of tiles)
MAP_WIDTH = 20
MAP_HEIGHT = 20
TILE_SIZE = 48  # Size of each tile in pixels

# Map generation parameters
BASE_WATER_RATIO = 0.225  # Fraction of map that starts as water (higher for smaller maps)
LAND_SMOOTH_PASSES = 5    # Number of smoothing passes for land/water (higher = smoother coastlines)
FOREST_RATIO = 0.18       # Fraction of land tiles to become forest
HILL_RATIO = 0.12         # Fraction of land tiles to become hills
MOUNTAIN_RATIO = 0.05     # Fraction of land tiles to become mountains
PLAINS_RATIO = 0.14       # Fraction of land tiles to become plains
SEED = None               # Random seed for reproducible map generation (set to an int for fixed maps)

# Terrain definitions: color and yields for each type
TERRAIN_TYPES: dict[str, dict[str, object]] = {
    "grassland": {"color": (170, 200, 170), "food": 2, "prod": 1},
    "plains":    {"color": (220, 220, 180), "food": 1, "prod": 2},
    "forest":    {"color": (120, 160, 120), "food": 1, "prod": 2},
    "hill":      {"color": (180, 150, 120), "food": 1, "prod": 2},
    "mountain":  {"color": (180, 180, 180), "food": 0, "prod": 0},
    "water":     {"color": (90, 140, 210), "food": 1, "prod": 0},
}

# Minimum spacing between cities
MIN_CITY_SPACING = 2
# Tile border color for grid lines
COLOR_TILE_BORDER = (180, 180, 180)