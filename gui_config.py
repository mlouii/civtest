"""
gui_config.py

This module contains GUI color and style constants.
- Defines colors, fonts, and UI element styles
- Centralizes GUI appearance for easy customization
All variables here are focused on visual style and theming.
"""
from config import TILE_SIZE

# gui_config.py
# Centralized color definitions for Civ MVP GUI

COLOR_BG = (0, 0, 0)
COLOR_TILE_HIGHLIGHT = (0, 255, 0)
COLOR_PATH_LINE = (0, 200, 255)
COLOR_PATH_ARROW = (0, 0, 0)
COLOR_INVALID_MOVE = (255, 0, 0)
COLOR_PANEL_BG = (230, 230, 240)
COLOR_PANEL_BORDER = (80, 80, 100)
COLOR_PLAYER_TEXT = (30, 30, 60)
COLOR_UNIT_TEXT = (0, 0, 0)
COLOR_UNIT_TEXT_ALT = (100, 0, 0)
COLOR_STATUS_TEXT = (0, 80, 0)
COLOR_BUTTON_BG = (180, 180, 220)
COLOR_BUTTON_BORDER = (80, 80, 100)
COLOR_BUTTON_TEXT = (30, 30, 60)
COLOR_INSTRUCTIONS = (30, 30, 60)

# UI and button constants
SIDEBAR_WIDTH = TILE_SIZE * 12
BUTTON_END_TURN = "end_turn"
BUTTON_FOUND_CITY = "found_city"
DEFAULT_PLAYER_ID = "P1"
DEFAULT_STATUS_MSGS = {
    "unit_deselected": "Unit deselected.",
    "city_deselected": "City deselected.",
    "turn_ended": "Turn ended.",
    "found_city": "Found City button clicked (implement logic)",
    "selected_city": "Selected city {name} at ({x},{y})",
    "selected_unit": "Selected {unit_type} at ({x},{y})",
    "invalid_move": "Invalid move: tile not allowed.",
    "invalid_move_points": "Invalid move: not enough movement points.",
    "invalid_path": "Invalid move: no path found."
}
