# main.py

import pygame
from map import GameMap
from config import MAP_WIDTH, MAP_HEIGHT, TILE_SIZE

def main():
    pygame.init()
    screen = pygame.display.set_mode(
        (TILE_SIZE * MAP_WIDTH, TILE_SIZE * MAP_HEIGHT)
    )
    pygame.display.set_caption("Civ MVP - Update/Render Loop")

    gmap = GameMap(MAP_WIDTH, MAP_HEIGHT)
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- UPDATE ---
        gmap.update(None)

        # --- RENDER ---
        screen.fill((0,0,0))
        gmap.render(screen)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
