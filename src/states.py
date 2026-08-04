from enum import Enum


class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    WIN = "win"


class GhostState(Enum):
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
