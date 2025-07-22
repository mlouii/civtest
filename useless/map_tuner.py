# map_tuner.py

import pygame
import pygame_gui
from map import GameMap
from config import MAP_WIDTH, MAP_HEIGHT, TILE_SIZE

pygame.init()
WINDOW_SIZE = (TILE_SIZE * MAP_WIDTH + 250, TILE_SIZE * MAP_HEIGHT)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Map Tuner")

manager = pygame_gui.UIManager(WINDOW_SIZE)

# Define slider configs
slider_specs = [
    {"label": "Water", "default": 0.35, "range": (0.0, 0.7), "format": "{:.2f}"},
    {"label": "Forest", "default": 0.18, "range": (0.0, 0.6), "format": "{:.2f}"},
    {"label": "Hills", "default": 0.12, "range": (0.0, 0.4), "format": "{:.2f}"},
    {"label": "Mountains", "default": 0.05, "range": (0.0, 0.2), "format": "{:.2f}"},
    {"label": "Plains", "default": 0.14, "range": (0.0, 0.4), "format": "{:.2f}"},
    {"label": "Smoothing", "default": 2, "range": (1, 5), "format": "{:d}"}
]

sliders = []
slider_texts = []

for i, spec in enumerate(slider_specs):
    label_surf = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect(TILE_SIZE*MAP_WIDTH + 20, 20 + i*60, 120, 24),
        text=spec["label"], manager=manager)
    slider = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect(TILE_SIZE*MAP_WIDTH + 20, 44 + i*60, 200, 24),
        start_value=spec["default"], value_range=spec["range"], manager=manager)
    if spec["label"] == "Smoothing":
        value_text = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(TILE_SIZE*MAP_WIDTH + 175, 20 + i*60, 50, 24),
            text=str(int(spec["default"])), manager=manager)
    else:
        value_text = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(TILE_SIZE*MAP_WIDTH + 175, 20 + i*60, 50, 24),
            text=spec["format"].format(spec["default"]), manager=manager)
    sliders.append(slider)
    slider_texts.append(value_text)

regen_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(TILE_SIZE*MAP_WIDTH + 50, 420, 140, 40),
    text="Regenerate Map", manager=manager)

clock = pygame.time.Clock()

def get_slider_vals():
    vals = [slider.get_current_value() for slider in sliders]
    # Unpack the list for clarity
    water, forest, hill, mountain, plains, smoothing = vals
    # Normalize land biomes so their sum never exceeds 1 - water
    land = 1.0 - water
    ratios = [water] + [v * land for v in (forest, hill, mountain, plains)]
    return ratios, int(smoothing)

def make_map_from_sliders():
    ratios, smoothing = get_slider_vals()
    return GameMap(
        MAP_WIDTH, MAP_HEIGHT,
        override_water=ratios[0],
        override_forest=ratios[1],
        override_hill=ratios[2],
        override_mountain=ratios[3],
        override_plains=ratios[4],
        override_smoothing=smoothing
    )

gmap = make_map_from_sliders()

running = True
while running:
    time_delta = clock.tick(30) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        manager.process_events(event)
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                for i, slider in enumerate(sliders):
                    if slider_specs[i]["label"] == "Smoothing":
                        slider_texts[i].set_text(str(int(slider.get_current_value())))
                    else:
                        slider_texts[i].set_text(slider_specs[i]["format"].format(slider.get_current_value()))
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == regen_button:
                    gmap = make_map_from_sliders()

    manager.update(time_delta)
    screen.fill((0, 0, 0))
    gmap.render(screen)
    manager.draw_ui(screen)
    pygame.display.flip()

pygame.quit()
