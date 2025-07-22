"""
city.py

This module contains city data, rendering, and management.
- Defines city attributes and population
- Handles city rendering and selection
- Manages city growth and production
All functions here are focused on city logic and visualization.
"""
from typing import Dict, Any, Type, Optional
import uuid

class City:
    def render(self, surface: Any, owner_color: Any = (0, 0, 0), selected: bool = False, font: Any = None) -> None:
        import pygame
        from config import TILE_SIZE
        px = self.x * TILE_SIZE + TILE_SIZE // 2
        py = self.y * TILE_SIZE + TILE_SIZE // 2
        radius = TILE_SIZE // 3
        # Draw city icon (filled circle)
        pygame.draw.circle(surface, owner_color, (px, py), radius)
        pygame.draw.circle(surface, (0, 0, 0), (px, py), radius, 2)  # Black outline
        # Draw city name below icon
        if font is None:
            font = pygame.font.SysFont(None, 22)
        name_surf = font.render(self.name, True, (0, 0, 0))
        name_rect = name_surf.get_rect(center=(px, py + radius + 12))
        surface.blit(name_surf, name_rect)
        # Highlight if selected
        if selected:
            pygame.draw.circle(surface, (0,255,255), (px, py), radius+6, 2)
    def __init__(
        self,
        owner_id: str,
        x: int,
        y: int,
        name: Optional[str] = None,
        city_id: Optional[str] = None,
        population: int = 1
    ) -> None:
        self.city_id: str = city_id if city_id is not None else str(uuid.uuid4())
        self.owner_id: str = owner_id
        self.x: int = x
        self.y: int = y
        self.population: int = population
        self.name: str = name if name is not None else f"City {self.city_id[-5:]}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "city_id": self.city_id,
            "owner_id": self.owner_id,
            "name": self.name,
            "population": self.population,
            "x": self.x,
            "y": self.y
        }

    @classmethod
    def from_dict(cls: Type['City'], data: Dict[str, Any]) -> 'City':
        return cls(
            owner_id=data["owner_id"],
            x=data["x"],
            y=data["y"],
            name=data.get("name"),
            city_id=data.get("city_id"),
            population=data.get("population", 1)
        )

    def __repr__(self) -> str:
        return (f"<City id={self.city_id} name={self.name} owner={self.owner_id} "
                f"pos=({self.x},{self.y}) pop={self.population}>")
