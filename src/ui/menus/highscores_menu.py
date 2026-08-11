import pygame
from typing import Optional
from states import GameState
from ui.menus.base_screen import BaseScreen


class HighscoresMenu(BaseScreen):
    """Manages the display of the score table."""

    def __init__(self, screen_width: int, screen_height: int):
        super().__init__(screen_width, screen_height)
        self.font = pygame.font.SysFont("Arial", 28, bold=True)
        self.COLOR_BG = (10, 10, 15)
        self.COLOR_TEXT = (255, 255, 255)

    def handle_event(self, event: pygame.event.Event) -> Optional[GameState]:
        """Press ESC to return to the main menu."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return GameState.MENU
        return GameState.HIGHSCORES

    def draw(self, surface: pygame.Surface) -> None:
        """Render the Highscores screen."""
        surface.fill(self.COLOR_BG)

        text = self.font.render("HIGH SCORES (Press ESC to return)",
                                True, self.COLOR_TEXT)
        rect = text.get_rect(center=(self.width // 2, self.height // 2))
        surface.blit(text, rect)
