from abc import ABC, abstractmethod
from typing import Optional
import pygame
from src.states import GameState


class BaseScreen(ABC):
    """A common interface and customizable graphical tools for any display."""

    COLOR_BG = (10, 10, 15)
    COLOR_LABEL = (160, 160, 170)
    COLOR_TEXT = (255, 255, 255)
    COLOR_TEXT1 = (220, 220, 220)
    COLOR_TITLE = (255, 255, 0)
    COLOR_BORDER = (33, 33, 222)
    COLOR_HEADER = (255, 183, 255)
    COLOR_DOT = (255, 183, 82)
    COLOR_CARD_BG = (15, 15, 25)
    COLOR_SELECTED = (255, 183, 255)
    COLOR_NORMAL = (200, 200, 210)
    COLOR_HIGHLIGHT = (40, 20, 50)
    COLOR_KEY_BG = (40, 40, 50)
    COLOR_KEY_BORDER = (0, 255, 255)

    def __init__(self, screen_width: int, screen_height: int):
        self.width = screen_width
        self.height = screen_height

        if not pygame.font.get_init():
            pygame.font.init()

        self.key_font = pygame.font.SysFont("Arial", 12, bold=True)

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> Optional[GameState]:
        """Processes native Pygame keyboard input."""
        pass

    def update(self) -> None:
        """Updates the screen's internal logic or animation (optional)."""
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the graphic content on the indicated surface."""
        pass

    def on_enter(self, previous_state: GameState) -> None:
        """Optional hook that runs every time the screen
        changes to this one."""
        pass

    def _draw_key_badge(self,
                        surface: pygame.Surface,
                        text: str,
                        x: int,
                        y: int) -> int:
        """A shared utility for designing stylish arcade-style buttons."""
        text_surf = self.key_font.render(text, True, (255, 255, 255))
        padding_x, padding_y = 6, 3
        width = text_surf.get_width() + (padding_x * 2)
        height = text_surf.get_height() + (padding_y * 2)

        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, (0, 0, 0), rect.move(2, 2), border_radius=4)
        pygame.draw.rect(surface, self.COLOR_KEY_BG, rect, border_radius=4)
        pygame.draw.rect(surface, self.COLOR_KEY_BORDER, rect,
                         width=1, border_radius=4)

        surface.blit(text_surf, (x + padding_x, y + padding_y))
        return width
