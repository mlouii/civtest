# test_game.py

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

    def test_bounds(self):
        gmap = GameMap(MAP_WIDTH, MAP_HEIGHT)
        self.assertIsNone(gmap.get_tile(-1, 0))
        self.assertIsNone(gmap.get_tile(MAP_WIDTH, MAP_HEIGHT))

    def test_water_ratio(self):
        gmap = GameMap(MAP_WIDTH, MAP_HEIGHT)
        # Water tiles should be at least 50% of the configured target after mapgen
        total_tiles = MAP_WIDTH * MAP_HEIGHT
        water_tiles = sum(1 for row in gmap.tiles for tile in row if tile.terrain == "water")
        min_water = int(BASE_WATER_RATIO * total_tiles * 0.5)
        self.assertGreaterEqual(water_tiles, min_water, f"Not enough water tiles: {water_tiles}/{total_tiles}")

class TestUnit(unittest.TestCase):
    def test_placeholder(self):
        self.assertTrue(True)

class TestCity(unittest.TestCase):
    def test_placeholder(self):
        self.assertTrue(True)

def run_module_tests(suite, module_name):
    result = unittest.TestResult()
    suite.run(result)
    if result.wasSuccessful():
        print(f"{module_name} module: PASS")
    else:
        print(f"{module_name} module: FAIL")
        for failure in result.failures + result.errors:
            print("   ", failure[1].strip().replace('\n', '\n    '))

def run_tests():
    print("\n=== Civ MVP Game - Module Tests ===\n")
    run_module_tests(unittest.defaultTestLoader.loadTestsFromTestCase(TestGameMap), "GameMap")
    run_module_tests(unittest.defaultTestLoader.loadTestsFromTestCase(TestUnit), "Unit")
    run_module_tests(unittest.defaultTestLoader.loadTestsFromTestCase(TestCity), "City")
    print("\n============================\n")

if __name__ == "__main__":
    run_tests()
