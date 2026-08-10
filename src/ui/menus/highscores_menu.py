import pygame
from typing import Optional
from states import GameState

class HighscoresMenu:
    """Manage the Scores screen."""
    def __init__(self, screen_width: int, screen_height: int):
        self.width = screen_width
        self.height = screen_height
        self.font = pygame.font.SysFont("Arial", 28, bold=True)
        self.COLOR_BG = (0, 0, 0)
        self.COLOR_TEXT = (255, 255, 255)

    def handle_event(self, event: pygame.event.Event) -> Optional[GameState]:
        """Wait for the user to press ESC to return to the menu."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return GameState.MENU
        return GameState.HIGHSCORES

    def draw(self, surface: pygame.Surface) -> None:
        """Render the Highscores screen."""
        surface.fill(self.COLOR_BG)
        
        text = self.font.render("MEJORES PUNTUACIONES (Pulsa ESC para volver)", True, self.COLOR_TEXT)
        rect = text.get_rect(center=(self.width // 2, self.height // 2))
        surface.blit(text, rect)