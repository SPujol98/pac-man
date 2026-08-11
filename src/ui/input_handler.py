from typing import Optional
import pygame
from states import Direction


class InputHandler:
    """Captures keyboard events and manages the buffer containing the
    address requested by the player."""

    def __init__(self):
        self.KEY_MAP = {
            pygame.K_UP: Direction.UP,
            pygame.K_w: Direction.UP,
            pygame.K_DOWN: Direction.DOWN,
            pygame.K_s: Direction.DOWN,
            pygame.K_LEFT: Direction.LEFT,
            pygame.K_a: Direction.LEFT,
            pygame.K_RIGHT: Direction.RIGHT,
            pygame.K_d: Direction.RIGHT,
        }
        self.buffered_direction: Optional[Direction] = None

    def process_event(self, event: pygame.event.Event) -> Optional[Direction]:
        """Process a Pygame event and update the address in the buffer."""
        if event.type == pygame.KEYDOWN:
            if event.key in self.KEY_MAP:
                self.buffered_direction = self.KEY_MAP[event.key]
                return self.buffered_direction
        return None

    def get_buffered_direction(self) -> Optional[Direction]:
        """Returns the direction the player has requested to take."""
        return self.buffered_direction

    def clear_buffer(self) -> None:
        """Clear the buffer once the character has completed the turn."""
        self.buffered_direction = None