"""
movement.py

This module contains movement, pathfinding, and validation logic.
- Computes valid moves and reachable tiles for units
- Implements pathfinding algorithms (e.g., BFS)
- Validates movement and city founding actions
All functions here are focused on unit movement and related rules.
"""
from typing import Tuple, List, Dict
from game import Game


# City founding validation logic
def can_found_city(game: 'Game', settler_unit: object, min_spacing: int = 2) -> bool:
    tile = game.map.get_tile(settler_unit.x, settler_unit.y)
    if not tile or getattr(tile, 'type', None) in ('water', 'mountain'):
        return False
    # No city exists on this tile
    for city in getattr(game, 'cities', []):
        if city.x == settler_unit.x and city.y == settler_unit.y:
            return False
    # No other city within minimum spacing
    for city in getattr(game, 'cities', []):
        if abs(city.x - settler_unit.x) <= min_spacing and abs(city.y - settler_unit.y) <= min_spacing:
            return False
    return True


# Pathfinding and movement logic for units
def compute_reachable(
    game: Game,
    unit: object
) -> Tuple[List[Tuple[int, int]], Dict[Tuple[int, int], List[Tuple[int, int]]]]:
    from config import MAP_WIDTH, MAP_HEIGHT
    start = (unit.x, unit.y)
    moves = unit.moves
    visited = set()
    valid_moves = []
    path_map = {}
    from collections import deque
    queue = deque()
    queue.append((start, [start], 0))
    visited.add(start)
    while queue:
        (cx, cy), path, dist = queue.popleft()
        if dist > 0:
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
                if tile.terrain != "water" and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(nx, ny)], dist+1))
    return valid_moves, path_map

# You can add more movement-related functions here as needed.
