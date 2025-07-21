# Map dimensions (number of tiles)
MAP_WIDTH = 20
MAP_HEIGHT = 20
TILE_SIZE = 48  # Size of each tile in pixels

# Map generation parameters
BASE_WATER_RATIO = 0.20   # Fraction of map that starts as water (higher for smaller maps)
LAND_SMOOTH_PASSES = 3    # Number of smoothing passes for land/water (higher = smoother coastlines)
FOREST_RATIO = 0.18       # Fraction of land tiles to become forest
HILL_RATIO = 0.12         # Fraction of land tiles to become hills
MOUNTAIN_RATIO = 0.05     # Fraction of land tiles to become mountains
PLAINS_RATIO = 0.14       # Fraction of land tiles to become plains
SEED = None               # Random seed for reproducible map generation (set to an int for fixed maps)