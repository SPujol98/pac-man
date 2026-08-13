from src.states import GameState
from src.ui.menus.base_score_entry import BaseScoreEntryScreen


class GameOverScreen(BaseScoreEntryScreen):
    """Screen displayed when the player runs out of lives or time."""

    def __init__(self, screen_width: int, screen_height: int) -> None:
        super().__init__(
            screen_width=screen_width,
            screen_height=screen_height,
            title="GAME OVER",
            title_color=(230, 40, 40),
            subtitle="Better luck next time!",
        )

    def handle_event(self, event):
        next_state = super().handle_event(event)
        return next_state or GameState.GAME_OVER


class WinScreen(BaseScoreEntryScreen):
    """Screen displayed when the player completes all the mazes."""

    def __init__(self, screen_width: int, screen_height: int) -> None:
        super().__init__(
            screen_width=screen_width,
            screen_height=screen_height,
            title="VICTORY!",
            title_color=(50, 230, 80),
            subtitle="Congratulations! You cleared the maze!",
        )

    def handle_event(self, event):
        next_state = super().handle_event(event)
        return next_state or GameState.WIN
