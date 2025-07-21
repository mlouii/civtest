from typing import Tuple, List, Dict, Optional
import pygame
from collections import deque
from game import Game
from map import GameMap
from config import MAP_WIDTH, MAP_HEIGHT, TILE_SIZE
from player import Player
def init_game() -> Game:
    player1 = Player(player_id="P1")
    players: Dict[str, Player] = {"P1": player1}
    return Game(game_map=GameMap(MAP_WIDTH, MAP_HEIGHT), players=players, current_player="P1")

def handle_events(
    game: Game,
    selected_unit: Optional[object],
    status_msg: str,
    valid_moves: List[Tuple[int, int]],
    path_map: Dict[Tuple[int, int], List[Tuple[int, int]]],
    end_turn_rect: pygame.Rect
) -> Tuple[bool, Optional[object], str, List[Tuple[int, int]], Dict[Tuple[int, int], List[Tuple[int, int]]]]:
    # ...existing code...
    running = True
    mouse_pos = pygame.mouse.get_pos()
    clicked = False
    # Ensure path_map is always initialized from the caller
    # (add path_map as a parameter to the function signature)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            clicked = True
            # End Turn button click
            if end_turn_rect.collidepoint(mouse_pos):
                for unit in game.units:
                    if unit.owner == game.current_player:
                        unit.reset_moves()
                game.next_turn()
                for unit in game.units:
                    unit.selected = False
                selected_unit = None
                status_msg = "Turn ended."
                valid_moves = []
                path_map = {}  # Reset only when turn ends
                continue
            # Map click
            mx, my = mouse_pos
            if mx < TILE_SIZE * MAP_WIDTH and my < TILE_SIZE * MAP_HEIGHT:
                tx = mx // TILE_SIZE
                ty = my // TILE_SIZE
                # If no unit selected, try to select one
                if not selected_unit:
                    for unit in game.units:
                        if unit.x == tx and unit.y == ty and unit.owner == game.current_player:
                            for u in game.units:
                                u.selected = False
                            unit.selected = True
                            selected_unit = unit
                            status_msg = f"Selected {unit.unit_type} at ({tx},{ty})"
                            # Compute all reachable tiles and paths using BFS
                            valid_moves, path_map = compute_reachable(game, unit)
                            break
                else:
                    # Try to move selected unit using pathfinding
                    if (tx, ty) in valid_moves:
                        path = path_map.get((tx, ty))
                        if path is not None:
                            if len(path)-1 <= selected_unit.moves:
                                # Move unit along path
                                for step in path[1:]:
                                    selected_unit.x, selected_unit.y = step
                                    selected_unit.moves -= 1
                                status_msg = f"Moved to ({tx},{ty})"
                                # Recompute reachable tiles
                                if selected_unit.moves > 0:
                                    valid_moves, path_map = compute_reachable(game, selected_unit)
                                else:
                                    selected_unit.selected = False
                                    selected_unit = None
                                    valid_moves = []
                                    path_map = {}
                            else:
                                status_msg = "Invalid move: not enough movement points."
                        else:
                            status_msg = "Invalid move: no path found."
                    else:
                        status_msg = "Invalid move: tile not allowed."
            else:
                if selected_unit:
                    selected_unit.selected = False
                    selected_unit = None
                    valid_moves = []
                    path_map = {}  # Reset only when unit is deselected
                    status_msg = "Unit deselected."
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                # End turn via keyboard
                for unit in game.units:
                    if unit.owner == game.current_player:
                        unit.reset_moves()
                game.next_turn()
                for unit in game.units:
                    unit.selected = False
                selected_unit = None
                status_msg = "Turn ended."
                valid_moves = []
                path_map = {}  # Reset only when turn ends
    return running, selected_unit, status_msg, valid_moves, path_map

def compute_reachable(
    game: Game,
    unit: object
) -> Tuple[List[Tuple[int, int]], Dict[Tuple[int, int], List[Tuple[int, int]]]]:
    # ...existing code...
    start = (unit.x, unit.y)
    moves = unit.moves
    visited = set()
    valid_moves = []
    path_map = {}
    queue = deque()
    queue.append((start, [start], 0))
    visited.add(start)
    while queue:
        (cx, cy), path, dist = queue.popleft()
        if dist > 0:
            # Only add to valid_moves if not occupied by another unit (except self)
            is_occupied = any(u.x == cx and u.y == cy and u != unit for u in game.units)
            if not is_occupied:
                valid_moves.append((cx, cy))
                path_map[(cx, cy)] = path.copy()
        if dist >= moves:
            continue
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = cx+dx, cy+dy
            if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                tile = game.map.get_tile(nx, ny)
                # Allow passing through occupied tiles, but not water
                if tile.terrain != "water" and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(nx, ny)], dist+1))
    # No fallback needed: valid_moves and path_map are always in sync
    return valid_moves, path_map

def update_game(game: Game) -> None:
    game.map.update(game)

def render_game(
    screen: pygame.Surface,
    game: Game,
    valid_moves: List[Tuple[int, int]],
    status_msg: str,
    end_turn_rect: pygame.Rect
) -> None:
    screen.fill((0,0,0))
    # Draw map and units
    game.map.render(screen, game)
    # Highlight valid move tiles
    # ...existing code...
    for (mx, my) in valid_moves:
        rect = pygame.Rect(mx*TILE_SIZE, my*TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, (0,255,0), rect, 3)
    # Optional: show path when hovering over a reachable tile
    mouse_pos = pygame.mouse.get_pos()
    mx, my = mouse_pos
    if valid_moves:
        tx = mx // TILE_SIZE
        ty = my // TILE_SIZE
        if (tx, ty) in valid_moves:
            # Draw path from selected unit to hovered tile
            selected_unit = next((u for u in game.units if getattr(u, 'selected', False)), None)
            if selected_unit:
                _, path_map = compute_reachable(game, selected_unit)
                path = path_map.get((tx, ty), [])
                for px, py in path:
                    rect = pygame.Rect(px*TILE_SIZE+TILE_SIZE//4, py*TILE_SIZE+TILE_SIZE//4, TILE_SIZE//2, TILE_SIZE//2)
                    pygame.draw.rect(screen, (0,200,255), rect, 0)
    # Draw status for invalid move (red highlight)
    if status_msg and status_msg.startswith("Invalid move"):
        mx, my = mouse_pos
        if mx < TILE_SIZE * MAP_WIDTH and my < TILE_SIZE * MAP_HEIGHT:
            tx = mx // TILE_SIZE
            ty = my // TILE_SIZE
            rect = pygame.Rect(tx*TILE_SIZE, ty*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, (255,0,0), rect, 3)
    # Draw GUI
    draw_gui(screen, game, status_msg, end_turn_rect)
def draw_gui(
    surface: pygame.Surface,
    game: Game,
    status_msg: Optional[str] = None,
    end_turn_rect: Optional[pygame.Rect] = None
) -> pygame.Rect:
    # ...existing code...
    # Sidebar dimensions
    panel_width = TILE_SIZE * 12
    # Make sidebar take up full screen height
    panel_height = surface.get_height()
    panel_x = TILE_SIZE * MAP_WIDTH
    panel_y = 0
    # Draw panel background
    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
    pygame.draw.rect(surface, (230, 230, 240), panel_rect)
    pygame.draw.rect(surface, (80, 80, 100), panel_rect, 2)

    # Font setup
    font = pygame.font.SysFont(None, 24)
    y = panel_y + 20
    x = panel_x + 20

    # Current player and turn
    player_str = f"Player: {game.current_player}"
    turn_str = f"Turn: {game.turn}"
    surface.blit(font.render(player_str, True, (30,30,60)), (x, y))
    y += 30
    surface.blit(font.render(turn_str, True, (30,30,60)), (x, y))
    y += 40

    # Selected unit info
    selected_unit = next((u for u in game.units if getattr(u, 'selected', False)), None)
    if selected_unit:
        surface.blit(font.render("Selected Unit:", True, (0,0,0)), (x, y))
        y += 25
        surface.blit(font.render(f"Type: {selected_unit.unit_type}", True, (0,0,0)), (x, y))
        y += 25
        surface.blit(font.render(f"Moves: {selected_unit.moves}", True, (0,0,0)), (x, y))
        y += 25
        surface.blit(font.render(f"Owner: {selected_unit.owner}", True, (0,0,0)), (x, y))
        y += 30
    else:
        surface.blit(font.render("No unit selected", True, (100,0,0)), (x, y))
        y += 40

    # Status message
    if status_msg:
        surface.blit(font.render(f"Status: {status_msg}", True, (0,80,0)), (x, y))
        y += 30

    # End Turn button
    button_w, button_h = 120, 40
    button_x = panel_x + 20
    button_y = panel_height - button_h - 20
    end_turn_rect = pygame.Rect(button_x, button_y, button_w, button_h)
    pygame.draw.rect(surface, (180, 180, 220), end_turn_rect)
    pygame.draw.rect(surface, (80, 80, 100), end_turn_rect, 2)
    btn_font = pygame.font.SysFont(None, 28)
    surface.blit(btn_font.render("End Turn", True, (30,30,60)), (button_x+10, button_y+8))

    # Instructions
    instructions = [
        "Controls:",
        "Click unit to select.",
        "Click tile to move.",
        "Press E or button to end turn."
    ]
    for line in instructions:
        surface.blit(font.render(line, True, (30,30,60)), (x, y))
        y += 25
    return end_turn_rect

def main() -> None:
    pygame.init()
    pygame.font.init()
    sidebar_width = TILE_SIZE * 12
    screen_width = TILE_SIZE * MAP_WIDTH + sidebar_width
    screen_height = TILE_SIZE * MAP_HEIGHT
    screen = pygame.display.set_mode(
        (screen_width, screen_height)
    )
    pygame.display.set_caption("Civ MVP - Update/Render Loop")

    game = init_game()
    clock = pygame.time.Clock()
    running = True
    selected_unit = None
    status_msg = ""
    valid_moves = []
    path_map = {}
    end_turn_rect = None

    # Initial draw to get button rect
    end_turn_rect = draw_gui(screen, game)

    while running:
        running, selected_unit, status_msg, valid_moves, path_map = handle_events(game, selected_unit, status_msg, valid_moves, path_map, end_turn_rect)
        update_game(game)
        end_turn_rect = draw_gui(screen, game)
        render_game(screen, game, valid_moves, status_msg, end_turn_rect)
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
