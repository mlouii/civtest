"""
main.py

This module contains the main game loop, event handling, and game state management.
- Initializes the game and main window
- Handles all user input and dispatches to modular event handlers
- Updates game state and triggers rendering
- Centralizes gameplay state via GameState
All functions here are focused on orchestrating gameplay, user interaction, and state updates.
"""
from typing import Tuple, List, Dict, Optional
from dataclasses import dataclass, field
import pygame
from collections import deque
from game import Game
from map import GameMap
from config import MAP_WIDTH, MAP_HEIGHT, TILE_SIZE
from player import Player
from movement import compute_reachable
from gui_config import (
    COLOR_BG, COLOR_TILE_HIGHLIGHT, COLOR_PATH_LINE, COLOR_PATH_ARROW, COLOR_INVALID_MOVE,
    COLOR_PANEL_BG, COLOR_PANEL_BORDER, COLOR_PLAYER_TEXT, COLOR_UNIT_TEXT, COLOR_UNIT_TEXT_ALT,
    COLOR_STATUS_TEXT, COLOR_BUTTON_BG, COLOR_BUTTON_BORDER, COLOR_BUTTON_TEXT, COLOR_INSTRUCTIONS,
    SIDEBAR_WIDTH, BUTTON_END_TURN, BUTTON_FOUND_CITY, DEFAULT_STATUS_MSGS
)
from gui import render_game, draw_gui
from gamestate import GameState
from unit import Unit



## GameState is now imported from gamestate.py


# Update game function (previously in main.py)
def update_game(game: Game) -> None:
    game.map.update(game)


def find_passable_tile(game_map: GameMap, preferred_coords: List[Tuple[int, int]]) -> Tuple[int, int]:
    """
    Returns the first passable tile from preferred_coords, or searches the map for any passable tile.
    """
    for x, y in preferred_coords:
        if game_map.is_tile_passable(x, y):
            return x, y
    # Fallback: search the map for any passable tile
    for y in range(game_map.height):
        for x in range(game_map.width):
            if game_map.is_tile_passable(x, y):
                return x, y
    # If no passable tile found, default to (0,0)
    return 0, 0

def init_game() -> Game:
    player1 = Player(player_id="P1")
    player2 = Player(player_id="P2")
    players: Dict[str, Player] = {"P1": player1, "P2": player2}
    from gui_config import PLAYER_COLORS
    player1.color = PLAYER_COLORS["P1"]
    player2.color = PLAYER_COLORS["P2"]
    game_map = GameMap(MAP_WIDTH, MAP_HEIGHT)
    # Find passable starting tiles for each player
    p1_start = find_passable_tile(game_map, [(2, 2)])
    p2_start = find_passable_tile(game_map, [(MAP_WIDTH-3, MAP_HEIGHT-3)])
    units = [
        Unit(unique_id=1, owner="P1", unit_type="settler", x=p1_start[0], y=p1_start[1]),
        Unit(unique_id=2, owner="P2", unit_type="settler", x=p2_start[0], y=p2_start[1])
    ]
    game = Game(game_map=game_map, players=players, units=units, current_player="P1")
    return game

def handle_quit_event() -> bool:
    return False

def handle_right_click(game: Game, state: GameState) -> None:
    if state.selected_unit:
        state.selected_unit.selected = False
        state.selected_unit = None
        state.valid_moves = []
        state.path_map = {}
        state.status_msg = "Unit deselected."
    if hasattr(game, "cities"):
        for city in game.cities:
            if getattr(city, "selected", False):
                city.selected = False
                state.status_msg = "City deselected."

def handle_left_click(game: Game, state: GameState, button_rects: Dict[str, Optional[pygame.Rect]], mouse_pos) -> bool:
    # Check all buttons
    for btn_name, btn_rect in button_rects.items():
        if btn_rect and btn_rect.collidepoint(mouse_pos):
            handle_button_click(btn_name, game, state)
            return True
    # Map click
    mx, my = mouse_pos
    if mx < TILE_SIZE * MAP_WIDTH and my < TILE_SIZE * MAP_HEIGHT:
        tx = mx // TILE_SIZE
        ty = my // TILE_SIZE
        if handle_city_selection(game, state, tx, ty):
            return True
        if handle_unit_selection(game, state, tx, ty):
            return True
        handle_unit_movement(game, state, tx, ty)
    else:
        handle_deselect_outside(game, state)
    return True

def end_turn_and_update_status(game: Game, state: GameState) -> None:
    state.selected_unit = None
    state.valid_moves = []
    state.path_map = {}
    for unit in game.units:
        unit.selected = False
    if hasattr(game, "cities"):
        for city in game.cities:
            city.selected = False
    round_advanced = game.end_turn_for_current_player()
    if round_advanced:
        state.status_msg = "All players ended turn. New round started."
    else:
        state.status_msg = f"{game.current_player} ended their turn."

def handle_button_click(btn_name: str, game: Game, state: GameState) -> None:
    if btn_name == BUTTON_END_TURN:
        for unit in game.units:
            if unit.owner == game.current_player:
                unit.reset_moves()
        end_turn_and_update_status(game, state)
    elif btn_name == BUTTON_FOUND_CITY:
        unit = state.selected_unit
        if unit:
            result = unit.found_city(game, state)
            # If city was founded, and no more units for this player, end turn automatically
            if result:
                player_units = [u for u in game.units if u.owner == game.current_player]
                if not player_units:
                    end_turn_and_update_status(game, state)
        else:
            state.status_msg = DEFAULT_STATUS_MSGS["invalid_move"]

def handle_city_selection(game: Game, state: GameState, tx: int, ty: int) -> bool:
    if hasattr(game, "cities"):
        for city in game.cities:
            if city.x == tx and city.y == ty:
                for c in game.cities:
                    c.selected = False
                city.selected = True
                state.selected_unit = None
                state.valid_moves = []
                state.path_map = {}
                state.status_msg = f"Selected city {city.name} at ({tx},{ty})"
                return True
    return False

def handle_unit_selection(game: Game, state: GameState, tx: int, ty: int) -> bool:
    if not state.selected_unit:
        for unit in game.units:
            if unit.x == tx and unit.y == ty and unit.owner == game.current_player:
                for u in game.units:
                    u.selected = False
                unit.selected = True
                state.selected_unit = unit
                state.status_msg = f"Selected {unit.unit_type} at ({tx},{ty})"
                state.valid_moves, state.path_map = compute_reachable(game, unit)
                return True
    return False

def handle_unit_movement(game: Game, state: GameState, tx: int, ty: int) -> None:
    if state.selected_unit and (tx, ty) in state.valid_moves:
        path = state.path_map.get((tx, ty))
        if path is not None:
            if len(path)-1 <= state.selected_unit.moves:
                for step in path[1:]:
                    state.selected_unit.x, state.selected_unit.y = step
                    state.selected_unit.moves -= 1
                state.status_msg = f"Moved to ({tx},{ty})"
                if state.selected_unit.moves > 0:
                    state.valid_moves, state.path_map = compute_reachable(game, state.selected_unit)
                else:
                    state.selected_unit.selected = False
                    state.selected_unit = None
                    state.valid_moves = []
                    state.path_map = {}
                    # Auto end turn if all units for current player have moved
                    round_ended = game.check_and_auto_end_turn()
                    if round_ended:
                        state.status_msg = "All units moved. Turn ended automatically."
            else:
                state.status_msg = "Invalid move: not enough movement points."
        else:
            state.status_msg = "Invalid move: no path found."
    elif state.selected_unit:
        state.status_msg = "Invalid move: tile not allowed."

def handle_deselect_outside(game: Game, state: GameState) -> None:
    if state.selected_unit:
        state.selected_unit.selected = False
        state.selected_unit = None
        state.valid_moves = []
        state.path_map = {}  # Reset only when unit is deselected
        state.status_msg = "Unit deselected."
    if hasattr(game, "cities"):
        for city in game.cities:
            if getattr(city, "selected", False):
                city.selected = False
                state.status_msg = "City deselected."

def handle_keydown_event(event, game: Game, state: GameState) -> None:
    if event.key == pygame.K_e:
        for unit in game.units:
            if unit.owner == game.current_player:
                unit.reset_moves()
        end_turn_and_update_status(game, state)

def handle_auto_end_turn(game: Game, state: GameState, running: bool) -> None:
    if hasattr(game, 'should_end_turn') and callable(game.should_end_turn):
        has_units = any(u.owner == game.current_player for u in getattr(game, 'units', []))
        if has_units and game.should_end_turn():
            game.next_turn()
            for unit in game.units:
                unit.selected = False
            state.selected_unit = None
            state.status_msg = "Turn ended (auto)."
            state.valid_moves = []
            state.path_map = {}

def handle_events(game: Game, state: GameState, button_rects: Dict[str, Optional[pygame.Rect]]) -> bool:
    running = True
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = handle_quit_event()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                handle_right_click(game, state)
            elif event.button == 1:
                running = handle_left_click(game, state, button_rects, mouse_pos)
        elif event.type == pygame.KEYDOWN:
            handle_keydown_event(event, game, state)
    handle_auto_end_turn(game, state, running)
    return running


def main() -> None:
    pygame.init()
    pygame.font.init()
    screen_width = TILE_SIZE * MAP_WIDTH + SIDEBAR_WIDTH
    screen_height = TILE_SIZE * MAP_HEIGHT
    screen = pygame.display.set_mode(
        (screen_width, screen_height)
    )
    pygame.display.set_caption("Civ MVP - Update/Render Loop")

    game = init_game()
    clock = pygame.time.Clock()
    running = True
    state = GameState()
    button_rects: Dict[str, Optional[pygame.Rect]] = draw_gui(screen, game, state.status_msg)

    while running:
        running = handle_events(game, state, button_rects)
        update_game(game)
        button_rects: Dict[str, Optional[pygame.Rect]] = draw_gui(screen, game, state.status_msg)
        render_game(screen, game, state)
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
