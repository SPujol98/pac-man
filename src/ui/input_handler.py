from typing import Optional
import pygame
from src.states import Direction


class InputHandler:
    """Translates arrow-key and WASD events into game Directions."""

    def __init__(self) -> None:
        self.key_map = {
            pygame.K_UP: Direction.UP,
            pygame.K_w: Direction.UP,
            pygame.K_DOWN: Direction.DOWN,
            pygame.K_s: Direction.DOWN,
            pygame.K_LEFT: Direction.LEFT,
            pygame.K_a: Direction.LEFT,
            pygame.K_RIGHT: Direction.RIGHT,
            pygame.K_d: Direction.RIGHT,
        }

    def process_event(self, event: pygame.event.Event) -> Optional[Direction]:
        """Convert a KEYDOWN event into a Direction, if mapped."""
        if event.type == pygame.KEYDOWN:
            return self.key_map.get(event.key)
        return None
