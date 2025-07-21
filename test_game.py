# test_game.py

import unittest
from map import GameMap, Tile, TERRAIN_TYPES
from config import MAP_WIDTH, MAP_HEIGHT, BASE_WATER_RATIO
from unit import Unit
from unit_config import UNIT_TYPES

class DummyMap:
    def is_tile_passable(self, x, y):
        return True

class BlockMap:
    def is_tile_passable(self, x, y):
        return False

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

        # Test center tile has 4 neighbors
        neighbors_center = gmap.neighbors(5, 5)
        self.assertEqual(len(neighbors_center), 4)

    def test_bounds(self):
        gmap = GameMap(MAP_WIDTH, MAP_HEIGHT)
        self.assertIsNone(gmap.get_tile(-1, 0))
        self.assertIsNone(gmap.get_tile(MAP_WIDTH, MAP_HEIGHT))
        self.assertIsNone(gmap.get_tile(MAP_WIDTH, 0))
        self.assertIsNone(gmap.get_tile(0, MAP_HEIGHT))


# --- Automated tests for multi-tile pathfinding movement ---
import types
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
        # 5x5 map, unit at (2,2), 3 moves, no obstacles
        game = DummyGame(5, 5)
        unit = PathfindingDummyUnit(2, 2, 3)
        valid_moves, path_map = compute_reachable(game, unit)
        # Should reach all tiles within 3 steps (no water, no occupied)
        self.assertIn((2, 5-1), valid_moves)  # edge
        self.assertIn((2, 0), valid_moves)
        self.assertIn((2, 3), valid_moves)
        self.assertIn((4, 2), valid_moves)
        self.assertGreaterEqual(len(valid_moves), 12)  # 13 tiles reachable in 3 steps

    def test_pathfinding_with_obstacles(self):
        # 5x5 map, water at (2,3), (3,2), unit at (2,2), 2 moves
        obstacles = {(2,3), (3,2)}
        game = DummyGame(5, 5, obstacles=obstacles)
        unit = PathfindingDummyUnit(2, 2, 2)
        valid_moves, path_map = compute_reachable(game, unit)
        self.assertNotIn((2,3), valid_moves)
        self.assertNotIn((3,2), valid_moves)
        # Should still reach (2,1), (1,2), (2,0), (0,2)
        self.assertIn((2,1), valid_moves)
        self.assertIn((1,2), valid_moves)

    def test_pathfinding_with_occupied_tiles(self):
        # 5x5 map, another unit at (2,3), unit at (2,2), 2 moves
        other_unit = PathfindingDummyUnit(2,3,3)
        game = DummyGame(5, 5, units=[other_unit])
        unit = PathfindingDummyUnit(2,2,2)
        valid_moves, path_map = compute_reachable(game, unit)
        self.assertNotIn((2,3), valid_moves)

    def test_move_unit_along_path(self):
        # Simulate moving unit from (2,2) to (2,4) with 2 moves
        game = DummyGame(5, 5)
        unit = PathfindingDummyUnit(2,2,2)
        valid_moves, path_map = compute_reachable(game, unit)
        dest = (2,4)
        path = path_map[dest]
        self.assertEqual(path, [(2,2),(2,3),(2,4)])
        self.assertEqual(len(path)-1, 2)
        # Simulate move
        for step in path[1:]:
            unit.x, unit.y = step
            unit.moves -= 1
        self.assertEqual((unit.x, unit.y), dest)
        self.assertEqual(unit.moves, 0)

    def test_invalid_move_feedback(self):
        # Try to move farther than allowed
        game = DummyGame(5, 5)
        unit = PathfindingDummyUnit(2,2,1)
        valid_moves, path_map = compute_reachable(game, unit)
        dest = (2,4)
        self.assertNotIn(dest, valid_moves)

    def test_unit_deselection_on_no_moves(self):
        # After moving, unit should be deselected if out of moves
        game = DummyGame(5, 5)
        unit = PathfindingDummyUnit(2,2,1)
        valid_moves, path_map = compute_reachable(game, unit)
        dest = (2,3)
        path = path_map[dest]
        for step in path[1:]:
            unit.x, unit.y = step
            unit.moves -= 1
        self.assertEqual(unit.moves, 0)


# --- main.py related tests ---
import pygame
from main import init_game, handle_events, update_game, render_game, draw_gui
from game import Game
from player import Player

class TestMainGame(unittest.TestCase):
    def setUp(self):
        self.game = init_game()

    def test_init_game_creates_game_instance(self):
        self.assertIsInstance(self.game, Game)
        self.assertEqual(self.game.current_player, "P1")
        self.assertIn("P1", self.game.players)

    def test_handle_events_quit(self):
        # Simulate QUIT event
        pygame.init()
        event = pygame.event.Event(pygame.QUIT)
        pygame.event.post(event)
        running = handle_events(self.game)
        self.assertFalse(running)
        pygame.quit()

    def test_update_game_calls_map_update(self):
        # Should not raise
        try:
            update_game(self.game)
        except Exception as e:
            self.fail(f"update_game raised {e}")

    def test_render_game_runs_without_error(self):
        pygame.init()
        from config import MAP_WIDTH, MAP_HEIGHT, TILE_SIZE
        sidebar_width = TILE_SIZE * 5
        screen = pygame.display.set_mode((TILE_SIZE * MAP_WIDTH + sidebar_width, TILE_SIZE * MAP_HEIGHT))
        try:
            render_game(screen, self.game)
        except Exception as e:
            self.fail(f"render_game raised {e}")
        pygame.quit()

    def test_draw_gui_runs_without_error(self):
        pygame.init()
        from config import MAP_WIDTH, MAP_HEIGHT, TILE_SIZE
        sidebar_width = TILE_SIZE * 5
        screen = pygame.display.set_mode((TILE_SIZE * MAP_WIDTH + sidebar_width, TILE_SIZE * MAP_HEIGHT))
        try:
            draw_gui(screen, self.game, status_msg="Test status")
        except Exception as e:
            self.fail(f"draw_gui raised {e}")
        pygame.quit()

    def test_water_ratio(self):
        gmap = GameMap(MAP_WIDTH, MAP_HEIGHT)
        # Water tiles should be at least 50% of the configured target after mapgen
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
        # There should be at least one tile of each terrain except possibly mountain
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

class TestUnit(unittest.TestCase):
    def setUp(self):
        self.unit = Unit(unique_id=1, owner="player1", unit_type="settler", x=2, y=3)

    def test_unit_creation(self):
        self.assertEqual(self.unit.unique_id, 1)
        self.assertEqual(self.unit.owner, "player1")
        self.assertEqual(self.unit.unit_type, "settler")
        self.assertEqual(self.unit.x, 2)
        self.assertEqual(self.unit.y, 3)
        self.assertEqual(self.unit.moves, UNIT_TYPES["settler"]["move_points"])
        self.assertEqual(self.unit.hp, UNIT_TYPES["settler"]["hp"])
        self.assertFalse(self.unit.selected)

    def test_unit_repr(self):
        rep = repr(self.unit)
        self.assertIn("Unit", rep)
        self.assertIn("settler", rep)
        self.assertIn("player1", rep)

    def test_unit_move_and_reset(self):
        moved = self.unit.move(2, 4, DummyMap())
        self.assertTrue(moved)
        self.assertEqual(self.unit.x, 2)
        self.assertEqual(self.unit.y, 4)
        self.assertEqual(self.unit.moves, UNIT_TYPES["settler"]["move_points"] - 1)
        self.unit.reset_moves()
        self.assertEqual(self.unit.moves, UNIT_TYPES["settler"]["move_points"])

    def test_unit_cannot_move_without_moves(self):
        self.unit.moves = 0
        moved = self.unit.move(2, 4, DummyMap())
        self.assertFalse(moved)

    def test_unit_can_move_validation(self):
        self.unit.moves = UNIT_TYPES["settler"]["move_points"]
        # Valid adjacent
        self.assertTrue(self.unit.can_move(2, 4, DummyMap()))
        # Not adjacent
        self.assertFalse(self.unit.can_move(4, 4, DummyMap()))
        # Not passable
        self.assertFalse(self.unit.can_move(2, 4, BlockMap()))

    def test_unit_to_dict(self):
        d = self.unit.to_dict()
        self.assertEqual(d["unique_id"], 1)
        self.assertEqual(d["owner"], "player1")
        self.assertEqual(d["unit_type"], "settler")
        self.assertEqual(d["x"], 2)
        self.assertEqual(d["y"], 3)
        self.assertEqual(d["moves"], UNIT_TYPES["settler"]["move_points"])
        self.assertEqual(d["hp"], UNIT_TYPES["settler"]["hp"])
        self.assertFalse(d["selected"])

    def test_unit_selection(self):
        self.unit.selected = True
        self.assertTrue(self.unit.selected)

    def test_unknown_unit_type_raises(self):
        with self.assertRaises(ValueError):
            Unit(unique_id=2, owner="player2", unit_type="unknown", x=0, y=0)

class TestCity(unittest.TestCase):
    def test_placeholder(self):
        self.assertTrue(True)
    # Add more tests when City class is implemented


# --- Game class tests ---
import sys
sys.path.append('.')  # Ensure local imports work
from game import Game
from player import Player

class DummyPlayer(Player):
    def __init__(self, name: str = "P1"):
        super().__init__(name)

class DummyUnit(Unit):
    def __init__(self, unique_id: int = 1, owner: str = "P1", unit_type: str = "settler", x: int = 0, y: int = 0):
        super().__init__(unique_id, owner, unit_type, x, y)

class DummyGameMap(GameMap):
    def __init__(self, width=10, height=10):
        super().__init__(width, height)
    def to_dict(self):
        return {"dummy": True}
    @classmethod
    def from_dict(cls, data):
        return cls()

class TestGameClass(unittest.TestCase):
    def setUp(self):
        self.map = DummyGameMap()
        self.unit1 = DummyUnit(unique_id=1, owner="P1", unit_type="settler", x=0, y=0)
        self.unit2 = DummyUnit(unique_id=2, owner="P2", unit_type="warrior", x=1, y=1)
        self.player1 = DummyPlayer(name="P1")
        self.player2 = DummyPlayer(name="P2")
        self.players = {"P1": self.player1, "P2": self.player2}
        self.game = Game(game_map=self.map, units=[self.unit1], players=self.players, current_player="P1", turn=1)

    def test_init(self):
        self.assertIsInstance(self.game.map, DummyGameMap)
        self.assertEqual(len(self.game.units), 1)
        self.assertEqual(list(self.game.players.keys()), ["P1", "P2"])
        self.assertEqual(self.game.current_player, "P1")
        self.assertEqual(self.game.turn, 1)

    def test_add_unit(self):
        self.game.add_unit(self.unit2)
        self.assertEqual(len(self.game.units), 2)
        self.assertIn(self.unit2, self.game.units)

    def test_remove_unit(self):
        self.game.add_unit(self.unit2)
        self.game.remove_unit(self.unit1)
        self.assertEqual(len(self.game.units), 1)
        self.assertNotIn(self.unit1, self.game.units)

    def test_add_player(self):
        player3 = DummyPlayer(name="P3")
        self.game.add_player("P3", player3)
        self.assertIn("P3", self.game.players)
        self.assertEqual(self.game.players["P3"], player3)

    def test_next_turn(self):
        self.game.next_turn()
        self.assertEqual(self.game.turn, 2)
        self.assertEqual(self.game.current_player, "P2")
        # Should rotate back to P1
        self.game.next_turn()
        self.assertEqual(self.game.current_player, "P1")


    def test_repr(self):
        r = repr(self.game)
        self.assertIn("Game", r)
        self.assertIn("turn=1", r)
        self.assertIn("current_player=P1", r)

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
    run_module_tests(unittest.defaultTestLoader.loadTestsFromTestCase(TestGameClass), "Game")
    run_module_tests(unittest.defaultTestLoader.loadTestsFromTestCase(TestPathfindingMovement), "PathfindingMovement")
    print("\n============================\n")

if __name__ == "__main__":
    run_tests()
