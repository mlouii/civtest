"""
gui.py

This module contains all rendering and GUI logic for the game, including:
- Drawing the game map, cities, units, and sidebar
- Rendering valid moves, paths, and invalid move highlights
- Drawing and managing sidebar buttons (e.g., End Turn, Found City)
- Modular sidebar rendering helpers
All functions here are focused on visual output and user interface elements.
"""
import pygame
from typing import Tuple, List, Dict, Optional
from gamestate import GameState
from game import Game
from gui_config import (
    COLOR_BG, COLOR_TILE_HIGHLIGHT, COLOR_PATH_LINE, COLOR_PATH_ARROW, COLOR_INVALID_MOVE,
    COLOR_PANEL_BG, COLOR_PANEL_BORDER, COLOR_PLAYER_TEXT, COLOR_UNIT_TEXT, COLOR_UNIT_TEXT_ALT,
    COLOR_STATUS_TEXT, COLOR_BUTTON_BG, COLOR_BUTTON_BORDER, COLOR_BUTTON_TEXT, COLOR_INSTRUCTIONS
)
from movement import compute_reachable
from config import MAP_WIDTH, MAP_HEIGHT, TILE_SIZE

def render_cities(screen: pygame.Surface, game: Game, state: GameState) -> None:
    if hasattr(game, "cities"):
        font = pygame.font.SysFont(None, 22)
        for city in game.cities:
            owner_color = (0, 0, 0)
            if city.owner_id in game.players and hasattr(game.players[city.owner_id], "color") and game.players[city.owner_id].color:
                owner_color = game.players[city.owner_id].color
            selected = getattr(city, "selected", False)
            city.render(screen, owner_color=owner_color, selected=selected, font=font)

def render_valid_moves(screen: pygame.Surface, state: GameState) -> None:
    for (mx, my) in state.valid_moves:
        rect = pygame.Rect(mx*TILE_SIZE, my*TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, COLOR_TILE_HIGHLIGHT, rect, 3)

def render_path(screen: pygame.Surface, game: Game, state: GameState) -> None:
    mouse_pos = pygame.mouse.get_pos()
    mx, my = mouse_pos
    if state.valid_moves:
        tx = mx // TILE_SIZE
        ty = my // TILE_SIZE
        if (tx, ty) in state.valid_moves:
            selected_unit = state.selected_unit
            if selected_unit:
                path = state.path_map.get((tx, ty), [])
                if len(path) > 1:
                    for i in range(len(path)-1):
                        x1 = path[i][0]*TILE_SIZE + TILE_SIZE//2
                        y1 = path[i][1]*TILE_SIZE + TILE_SIZE//2
                        x2 = path[i+1][0]*TILE_SIZE + TILE_SIZE//2
                        y2 = path[i+1][1]*TILE_SIZE + TILE_SIZE//2
                        pygame.draw.line(screen, COLOR_PATH_ARROW, (x1, y1), (x2, y2), 4)
                    end_x = path[-1][0]*TILE_SIZE + TILE_SIZE//2
                    end_y = path[-1][1]*TILE_SIZE + TILE_SIZE//2
                    dx = end_x - (path[-2][0]*TILE_SIZE + TILE_SIZE//2)
                    dy = end_y - (path[-2][1]*TILE_SIZE + TILE_SIZE//2)
                    length = max((dx**2 + dy**2)**0.5, 1)
                    ux, uy = dx/length, dy/length
                    arrow_size = 12
                    perp_x, perp_y = -uy, ux
                    tip_x = end_x + ux*2
                    tip_y = end_y + uy*2
                    base_x = end_x - ux*arrow_size
                    base_y = end_y - uy*arrow_size
                    p1 = (tip_x, tip_y)
                    p2 = (base_x + perp_x*arrow_size//2, base_y + perp_y*arrow_size//2)
                    p3 = (base_x - perp_x*arrow_size//2, base_y - perp_y*arrow_size//2)
                    pygame.draw.polygon(screen, COLOR_PATH_ARROW, [p1, p2, p3])
                    pygame.draw.line(screen, COLOR_PATH_ARROW, (path[-2][0]*TILE_SIZE + TILE_SIZE//2, path[-2][1]*TILE_SIZE + TILE_SIZE//2), (base_x, base_y), 6)

def render_invalid_move(screen: pygame.Surface, game: Game, state: GameState) -> None:
    selected_unit = state.selected_unit
    mouse_pos = pygame.mouse.get_pos()
    mx, my = mouse_pos
    if selected_unit:
        if mx < TILE_SIZE * MAP_WIDTH and my < TILE_SIZE * MAP_HEIGHT:
            tx = mx // TILE_SIZE
            ty = my // TILE_SIZE
            if (tx, ty) not in state.valid_moves:
                rect = pygame.Rect(tx*TILE_SIZE, ty*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, COLOR_INVALID_MOVE, rect, 3)

def render_game(
    screen: pygame.Surface,
    game: Game,
    state: GameState
) -> None:
    screen.fill(COLOR_BG)
    game.map.render(screen, game)
    render_cities(screen, game, state)
    render_valid_moves(screen, state)
    render_path(screen, game, state)
    render_invalid_move(screen, game, state)
    draw_gui(screen, game, state.status_msg)

def draw_sidebar_panel(surface):
    panel_width = TILE_SIZE * 12
    panel_height = surface.get_height()
    panel_x = TILE_SIZE * MAP_WIDTH
    panel_y = 0
    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
    pygame.draw.rect(surface, COLOR_PANEL_BG, panel_rect)
    pygame.draw.rect(surface, COLOR_PANEL_BORDER, panel_rect, 2)
    return panel_x, panel_y, panel_width, panel_height

def draw_player_info(surface, game, font, x, y):
    player_str = f"Player: {game.current_player}"
    turn_str = f"Turn: {game.turn}"
    surface.blit(font.render(player_str, True, COLOR_PLAYER_TEXT), (x, y))
    y += 30
    surface.blit(font.render(turn_str, True, COLOR_PLAYER_TEXT), (x, y))
    y += 40
    return y

def draw_selected_info(surface, game, font, x, y):
    selected_unit = next((u for u in game.units if getattr(u, 'selected', False)), None)
    selected_city = None
    found_city_rect = None
    if hasattr(game, "cities"):
        selected_city = next((c for c in game.cities if getattr(c, "selected", False)), None)
    if selected_city:
        name_font = pygame.font.SysFont(None, 32, bold=True)
        surface.blit(name_font.render(selected_city.name, True, COLOR_UNIT_TEXT), (x, y))
        y += 35
        surface.blit(font.render(f"Owner: {selected_city.owner_id}", True, COLOR_UNIT_TEXT), (x, y))
        y += 25
        surface.blit(font.render(f"Population: {selected_city.population}", True, COLOR_UNIT_TEXT), (x, y))
        y += 25
        surface.blit(font.render(f"Location: ({selected_city.x}, {selected_city.y})", True, COLOR_UNIT_TEXT), (x, y))
        y += 30
    elif selected_unit:
        surface.blit(font.render("Selected Unit:", True, COLOR_UNIT_TEXT), (x, y))
        y += 25
        surface.blit(font.render(f"Type: {selected_unit.unit_type}", True, COLOR_UNIT_TEXT), (x, y))
        y += 25
        surface.blit(font.render(f"Moves: {selected_unit.moves}", True, COLOR_UNIT_TEXT), (x, y))
        y += 25
        surface.blit(font.render(f"Owner: {selected_unit.owner}", True, COLOR_UNIT_TEXT), (x, y))
        y += 30
        from movement import can_found_city
        if selected_unit.unit_type == "settler" and can_found_city(game, selected_unit):
            button_w, button_h = 140, 40
            button_x = x
            button_y = y
            found_city_rect = pygame.Rect(button_x, button_y, button_w, button_h)
            pygame.draw.rect(surface, COLOR_BUTTON_BG, found_city_rect)
            pygame.draw.rect(surface, COLOR_BUTTON_BORDER, found_city_rect, 2)
            btn_font = pygame.font.SysFont(None, 28)
            surface.blit(btn_font.render("Found City", True, COLOR_BUTTON_TEXT), (button_x+10, button_y+8))
            y += button_h + 10
    else:
        surface.blit(font.render("No unit/city selected", True, COLOR_UNIT_TEXT_ALT), (x, y))
        y += 40
    return y, found_city_rect

def draw_status(surface, status_msg, font, x, y):
    if status_msg:
        surface.blit(font.render(f"Status: {status_msg}", True, COLOR_STATUS_TEXT), (x, y))
        y += 30
    return y

def draw_end_turn_button(surface, panel_x, panel_height):
    button_w, button_h = 120, 40
    button_x = panel_x + 20
    button_y = panel_height - button_h - 20
    end_turn_button_rect = pygame.Rect(button_x, button_y, button_w, button_h)
    pygame.draw.rect(surface, COLOR_BUTTON_BG, end_turn_button_rect)
    pygame.draw.rect(surface, COLOR_BUTTON_BORDER, end_turn_button_rect, 2)
    btn_font = pygame.font.SysFont(None, 28)
    surface.blit(btn_font.render("End Turn", True, COLOR_BUTTON_TEXT), (button_x+10, button_y+8))
    return end_turn_button_rect

def draw_instructions(surface, font, x, y):
    instructions = [
        "Controls:",
        "Click unit to select.",
        "Click tile to move.",
        "Press E or button to end turn."
    ]
    for line in instructions:
        surface.blit(font.render(line, True, COLOR_INSTRUCTIONS), (x, y))
        y += 25
    return y

def draw_gui(surface: pygame.Surface, game: Game, status_msg: Optional[str] = None) -> Dict[str, pygame.Rect]:
    panel_x, panel_y, panel_width, panel_height = draw_sidebar_panel(surface)
    font = pygame.font.SysFont(None, 24)
    y = panel_y + 20
    x = panel_x + 20
    y = draw_player_info(surface, game, font, x, y)
    y, found_city_rect = draw_selected_info(surface, game, font, x, y)
    y = draw_status(surface, status_msg, font, x, y)
    end_turn_button_rect = draw_end_turn_button(surface, panel_x, panel_height)
    y = draw_instructions(surface, font, x, y)
    return {"end_turn": end_turn_button_rect, "found_city": found_city_rect}
