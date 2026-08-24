from src.states import GameState
import pygame
from src.ui.menus.base_score_entry import BaseScoreEntryScreen


class GameOverScreen(BaseScoreEntryScreen):
    """Screen displayed when the player runs out of lives or time."""

    def __init__(self, screen_width: int, screen_height: int,
                 highscore_file: str = "highscores.json") -> None:
        super().__init__(
            screen_width=screen_width,
            screen_height=screen_height,
            title="GAME OVER",
            title_color=(255, 46, 99),
            subtitle="Better luck next time!",
            highscore_file=highscore_file
        )

    def handle_event(self, event: pygame.event.Event) -> GameState:
        """Delegate to the base handler, defaulting to this same state."""
        next_state = super().handle_event(event)
        return next_state or GameState.GAME_OVER


class WinScreen(BaseScoreEntryScreen):
    """Screen displayed when the player completes all the mazes."""

    def __init__(self, screen_width: int, screen_height: int,
                 highscore_file: str = "highscores.json") -> None:
        super().__init__(
            screen_width=screen_width,
            screen_height=screen_height,
            title="VICTORY!",
            title_color=(57, 255, 178),
            subtitle="Congratulations! You cleared the maze!",
            highscore_file=highscore_file
        )

    def handle_event(self, event: pygame.event.Event) -> GameState:
        """Delegate to the base handler, defaulting to this same state."""
        next_state = super().handle_event(event)
        return next_state or GameState.WIN
