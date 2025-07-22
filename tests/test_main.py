"""
test_main.py

This file tests main game logic, including:
- Starting tile selection and validation
- Ensuring tiles are not trapped
- Distinctness and fallback logic for starting tiles
"""
import unittest
import pygame
from main import init_game, handle_events, update_game, render_game, draw_gui
from game import Game
from player import Player

class TestMainGame(unittest.TestCase):
    def test_starting_tiles_are_not_trapped(self):
        from map import GameMap
        from game import Game
        from player import Player
        from config import MAP_WIDTH, MAP_HEIGHT
        game_map = GameMap(MAP_WIDTH, MAP_HEIGHT)
        player = Player(player_id="P1")
        players = {"P1": player}
        game = Game(game_map=game_map, players=players, current_player="P1")
        start_tiles = game._find_starting_tiles(2)
        for x, y in start_tiles:
            self.assertTrue(game_map.is_tile_passable(x, y))
            neighbors = game_map.neighbors(x, y)
            self.assertTrue(any(game_map.is_tile_passable(n.x, n.y) for n in neighbors),
                            f"Tile ({x},{y}) is trapped!")

    def test_starting_tiles_are_distinct(self):
        from map import GameMap
        from game import Game
        from player import Player
        from config import MAP_WIDTH, MAP_HEIGHT
        game_map = GameMap(MAP_WIDTH, MAP_HEIGHT)
        player = Player(player_id="P1")
        players = {"P1": player}
        game = Game(game_map=game_map, players=players, current_player="P1")
        start_tiles = game._find_starting_tiles(2)
        self.assertEqual(len(set(start_tiles)), 2)

    def test_fallback_tiles(self):
        from map import GameMap
        from game import Game
        from player import Player
        from config import MAP_WIDTH, MAP_HEIGHT
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
        player = Player(player_id="P1")
        players = {"P1": player}
        game = Game(game_map=blocked_map, players=players, current_player="P1")
        start_tiles = game._find_starting_tiles(2)
        self.assertIn((0,0), start_tiles)
        self.assertIn((1,0), start_tiles)
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
        from gamestate import GameState
        button_rects = {}
        state = GameState(self.game)
        running = handle_events(self.game, state, button_rects)
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
        from gamestate import GameState
        state = GameState(self.game)
        try:
            render_game(screen, self.game, state)
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

if __name__ == "__main__":
    unittest.main()
