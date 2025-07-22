"""
test_map.py

This file tests the GameMap and Tile logic, including:
- Tile creation and bounds
- Terrain distribution and attributes
- Neighbor logic
"""
import unittest
from map import GameMap, Tile, TERRAIN_TYPES
from config import MAP_WIDTH, MAP_HEIGHT, BASE_WATER_RATIO

class TestGameMap(unittest.TestCase):
    def test_tile_creation(self):
        gmap = GameMap(MAP_WIDTH, MAP_HEIGHT)
        tile = gmap.get_tile(2, 3)
        self.assertIsInstance(tile, Tile)
        self.assertIn(tile.terrain, TERRAIN_TYPES)

    def test_neighbors(self):
        gmap = GameMap(MAP_WIDTH, MAP_HEIGHT)
        neighbors = gmap.neighbors(0, 0)
        self.assertTrue(all(isinstance(n, Tile) for n in neighbors))
        self.assertEqual(len(neighbors), 2)  # corner should have 2
        neighbors_center = gmap.neighbors(5, 5)
        self.assertEqual(len(neighbors_center), 4)

    def test_bounds(self):
        gmap = GameMap(MAP_WIDTH, MAP_HEIGHT)
        self.assertIsNone(gmap.get_tile(-1, 0))
        self.assertIsNone(gmap.get_tile(MAP_WIDTH, MAP_HEIGHT))
        self.assertIsNone(gmap.get_tile(MAP_WIDTH, 0))
        self.assertIsNone(gmap.get_tile(0, MAP_HEIGHT))

    def test_water_ratio(self):
        gmap = GameMap(MAP_WIDTH, MAP_HEIGHT)
        total_tiles = MAP_WIDTH * MAP_HEIGHT
        water_tiles = sum(1 for row in gmap.tiles for tile in row if tile.terrain == "water")
        min_water = int(BASE_WATER_RATIO * total_tiles * 0.5)
        self.assertGreaterEqual(water_tiles, min_water, f"Not enough water tiles: {water_tiles}/{total_tiles}")

    def test_terrain_distribution(self):
        gmap = GameMap(MAP_WIDTH, MAP_HEIGHT)
        terrain_counts = {key: 0 for key in TERRAIN_TYPES}
        for row in gmap.tiles:
            for tile in row:
                terrain_counts[tile.terrain] += 1
        for terrain in ["grassland", "plains", "forest", "hill", "water"]:
            self.assertGreater(terrain_counts[terrain], 0, f"No tiles of terrain: {terrain}")

    def test_tile_attributes(self):
        gmap = GameMap(MAP_WIDTH, MAP_HEIGHT)
        tile = gmap.get_tile(0, 0)
        self.assertTrue(hasattr(tile, "x"))
        self.assertTrue(hasattr(tile, "y"))
        self.assertTrue(hasattr(tile, "terrain"))
        self.assertTrue(hasattr(tile, "city"))
        self.assertTrue(hasattr(tile, "unit"))
        self.assertIn(tile.terrain, TERRAIN_TYPES)
        self.assertIsInstance(tile.color, tuple)

if __name__ == "__main__":
    unittest.main()
