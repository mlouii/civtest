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
    "grassland": {"color": (50, 200, 50), "food": 2, "prod": 1},
    "plains":    {"color": (200, 200, 100), "food": 1, "prod": 2},
    "forest":    {"color": (34, 139, 34),   "food": 1, "prod": 2},
    "hill":      {"color": (139, 69, 19),   "food": 1, "prod": 2},
    "mountain":  {"color": (110, 110, 110), "food": 0, "prod": 0},
    "water":     {"color": (65, 105, 225),  "food": 1, "prod": 0},
}