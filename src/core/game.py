from __future__ import annotations
from src.entities.player import Player
from src.entities.ghost import Ghost
from src.states import GhostState
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.level import Level


class Game:
    """The main game controller
    orchestrating logic, entities, and the game loop."""

    def __init__(self, level: Level, lives: int) -> None:
        self.level = level
        self.is_running: bool = True
        self.score: int = 0
        self.lives = lives

        self.player = Player(self.level.player_spawn, 5.0, self.lives)
        g_spawn1, g_spawn2, g_spawn3, g_spawn4 = self.level.ghost_spawns
        c1, c2, c3, c4 = self.level.superpacgum_spawns
        self.ghosts = [
            Ghost(g_spawn1, "blinky", 4.5, c2),
            Ghost(g_spawn2, "pinky", 4.5, c1),
            Ghost(g_spawn3, "inky", 4.5, c4),
            Ghost(g_spawn4, "clyde", 4.5, c3)
        ]

    def _handle_events(self) -> None:
        """Process keyboard and window events."""
        pass

    def _update(self, dt: float) -> None:
        """Update game logic, entity positions, and collisions."""
        self.level.update(dt)
        self.player.update(dt, self.level)
        for gh in self.ghosts:
            gh.update(dt, self.level, self.player)
        for item in self.level.collectibles[:]:
            if item.cell == self.player.cell:
                self.score += item.points
                self.level.collectibles.remove(item)
                if item.sprite_id == "superpacgum":
                    for gh in self.ghosts:
                        gh.state = GhostState.FRIGHTENED
        if (self.level.is_completed() or self.level.time_left <= 0
                or self.lives <= 0):
            self.is_running = False

    def _render(self) -> None:
        """Draw the current game state to the screen."""
        pass

    def run(self) -> None:
        """The main Game Loop."""
        while self.is_running:
            self._handle_events()
            self._update(0.016)
            self._render()
        print("Game Finished!")
        print(f"Finally score: {self.score}")
