"""
test_pathfinding.py

This file tests pathfinding and movement logic, including:
- BFS reachable tiles
- Pathfinding with obstacles and occupied tiles
- Move simulation and feedback
"""
import unittest
from main import compute_reachable

class PathfindingDummyUnit:
    def __init__(self, x, y, moves):
        self.x = x
        self.y = y
        self.moves = moves
        self.unit_type = "settler"
        self.owner = "P1"

class DummyTile:
    def __init__(self, terrain="grassland"):
        self.terrain = terrain

class DummyGame:
    def __init__(self, width, height, obstacles=None, units=None):
        import types
        self.map = types.SimpleNamespace()
        self.map.get_tile = self.get_tile
        self.units = units if units else []
        self.width = width
        self.height = height
        self.obstacles = obstacles if obstacles else set()
    def get_tile(self, x, y):
        if (x, y) in self.obstacles:
            return DummyTile(terrain="water")
        return DummyTile(terrain="grassland")

class TestPathfindingMovement(unittest.TestCase):
    def test_bfs_reachable_tiles(self):
        game = DummyGame(5, 5)
        unit = PathfindingDummyUnit(2, 2, 3)
        valid_moves, path_map = compute_reachable(game, unit)
        self.assertIn((2, 5-1), valid_moves)
        self.assertIn((2, 0), valid_moves)
        self.assertIn((2, 3), valid_moves)
        self.assertIn((4, 2), valid_moves)
        self.assertGreaterEqual(len(valid_moves), 12)

    def test_pathfinding_with_obstacles(self):
        obstacles = {(2,3), (3,2)}
        game = DummyGame(5, 5, obstacles=obstacles)
        unit = PathfindingDummyUnit(2, 2, 2)
        valid_moves, path_map = compute_reachable(game, unit)
        self.assertNotIn((2,3), valid_moves)
        self.assertNotIn((3,2), valid_moves)
        self.assertIn((2,1), valid_moves)
        self.assertIn((1,2), valid_moves)

    def test_pathfinding_with_occupied_tiles(self):
        other_unit = PathfindingDummyUnit(2,3,3)
        game = DummyGame(5, 5, units=[other_unit])
        unit = PathfindingDummyUnit(2,2,2)
        valid_moves, path_map = compute_reachable(game, unit)
        self.assertNotIn((2,3), valid_moves)

    def test_move_unit_along_path(self):
        game = DummyGame(5, 5)
        unit = PathfindingDummyUnit(2,2,2)
        valid_moves, path_map = compute_reachable(game, unit)
        dest = (2,4)
        path = path_map[dest]
        self.assertEqual(path, [(2,2),(2,3),(2,4)])
        self.assertEqual(len(path)-1, 2)
        for step in path[1:]:
            unit.x, unit.y = step
            unit.moves -= 1
        self.assertEqual((unit.x, unit.y), dest)
        self.assertEqual(unit.moves, 0)

    def test_invalid_move_feedback(self):
        game = DummyGame(5, 5)
        unit = PathfindingDummyUnit(2,2,1)
        valid_moves, path_map = compute_reachable(game, unit)
        dest = (2,4)
        self.assertNotIn(dest, valid_moves)

    def test_unit_deselection_on_no_moves(self):
        game = DummyGame(5, 5)
        unit = PathfindingDummyUnit(2,2,1)
        valid_moves, path_map = compute_reachable(game, unit)
        dest = (2,3)
        path = path_map[dest]
        for step in path[1:]:
            unit.x, unit.y = step
            unit.moves -= 1
        self.assertEqual(unit.moves, 0)

# --- City founding logic from test_movement.py ---
from movement import can_found_city
from game import Game
from map import GameMap
from unit import Unit
from city import City
from player import Player

class TestCanFoundCity(unittest.TestCase):
    def setUp(self):
        from config import MAP_WIDTH, MAP_HEIGHT
        self.game = Game(game_map=GameMap(MAP_WIDTH, MAP_HEIGHT))
        self.player = Player("P1")
        self.game.add_player("P1", self.player)
        # Assume map is MAP_WIDTH x MAP_HEIGHT and all tiles are land by default
        for x in range(self.game.map.width):
            for y in range(self.game.map.height):
                tile = self.game.map.get_tile(x, y)
                tile.type = "land"
        # Place a settler at (5,5)
        self.settler = Unit(unique_id=1, owner="P1", unit_type="settler", x=5, y=5)
        self.game.add_unit(self.settler)

    def test_valid_tile(self):
        # No cities, tile is land
        self.assertTrue(can_found_city(self.game, self.settler))

    def test_tile_is_water(self):
        self.game.map.get_tile(5, 5).type = "water"
        self.assertFalse(can_found_city(self.game, self.settler))

    def test_tile_is_mountain(self):
        self.game.map.get_tile(5, 5).type = "mountain"
        self.assertFalse(can_found_city(self.game, self.settler))

    def test_city_on_tile(self):
        city = City(owner_id="P1", x=5, y=5)
        self.game.add_city(city)
        self.assertFalse(can_found_city(self.game, self.settler))

    def test_city_too_close(self):
        city = City(owner_id="P1", x=6, y=5)
        self.game.add_city(city)
        self.assertFalse(can_found_city(self.game, self.settler))

    def test_city_far_enough(self):
        city = City(owner_id="P1", x=8, y=8)
        self.game.add_city(city)
        self.assertTrue(can_found_city(self.game, self.settler))
if __name__ == "__main__":
    unittest.main()
