from enum import Enum


class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    WIN = "win"
    HIGHSCORES = "highscores"
    INSTRUCTIONS = "instructions"
    QUIT = "quit"


class GhostState(Enum):
    SCATTER = "scatter"
    CHASE = "chase"
    FRIGHTENED = "frightened"
    EATEN = "eaten"


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    def __init__(self, dx: int, dy: int) -> None:
        self.dx = dx
        self.dy = dy

    def opposite(self) -> "Direction":
        """Returns the opposite direction to prevent
        ghosts from turning back."""
        match self:
            case Direction.UP:
                return Direction.DOWN
            case Direction.DOWN:
                return Direction.UP
            case Direction.LEFT:
                return Direction.RIGHT
            case Direction.RIGHT:
                return Direction.LEFT
            case _:
                raise ValueError(f"Unknown direction: {self}")
