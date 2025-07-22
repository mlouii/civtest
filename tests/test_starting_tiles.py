"""
test_starting_tiles.py

This file tests starting tile logic, including:
- Passability and neighbor checks for starting tiles
- Distinctness of starting tiles
- Fallback logic when few tiles are available
"""
import unittest
from game import Game
from map import GameMap
from config import MAP_WIDTH, MAP_HEIGHT
from player import Player
from unit import Unit

class TestStartingTiles(unittest.TestCase):
    def setUp(self):
        self.game_map = GameMap(MAP_WIDTH, MAP_HEIGHT)
        self.player = Player(player_id="P1")
        self.players = {"P1": self.player}

    def test_starting_tiles_are_not_trapped(self):
        game = Game(game_map=self.game_map, players=self.players, current_player="P1")
        start_tiles = game._find_starting_tiles(2)
        for x, y in start_tiles:
            self.assertTrue(self.game_map.is_tile_passable(x, y))
            neighbors = self.game_map.neighbors(x, y)
            self.assertTrue(any(self.game_map.is_tile_passable(n.x, n.y) for n in neighbors),
                            f"Tile ({x},{y}) is trapped!")

    def test_starting_tiles_are_distinct(self):
        game = Game(game_map=self.game_map, players=self.players, current_player="P1")
        start_tiles = game._find_starting_tiles(2)
        self.assertEqual(len(set(start_tiles)), 2)

    def test_fallback_tiles(self):
        # Simulate a map with no passable tiles except (0,0) and (1,0)
        class BlockedMap(GameMap):
            def is_tile_passable(self, x, y):
                return (x, y) in [(0,0), (1,0)]
            def neighbors(self, x, y):
                # Only allow (0,0) and (1,0) to be neighbors of each other
                if (x, y) == (0,0):
                    return [self.get_tile(1,0)]
                if (x, y) == (1,0):
                    return [self.get_tile(0,0)]
                return []
        blocked_map = BlockedMap(MAP_WIDTH, MAP_HEIGHT)
        game = Game(game_map=blocked_map, players=self.players, current_player="P1")
        start_tiles = game._find_starting_tiles(2)
        self.assertIn((0,0), start_tiles)
        self.assertIn((1,0), start_tiles)

if __name__ == "__main__":
    unittest.main()
