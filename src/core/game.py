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
        self.wave_timer: float = 7.0
        self.frightened_timer: float = 0.0
        self.global_state: GhostState = GhostState.SCATTER

        self.player = Player(self.level.player_spawn, 5.0, lives)
        g_spawn1, g_spawn2, g_spawn3, g_spawn4 = self.level.ghost_spawns
        c1, c2, c3, c4 = self.level.superpacgum_spawns
        self.ghosts = [
            Ghost(g_spawn1, "blinky", self.player.speed - 0.5, c2,
                  self.level.ghost_points),
            Ghost(g_spawn2, "pinky", self.player.speed - 0.5, c1,
                  self.level.ghost_points),
            Ghost(g_spawn3, "inky", self.player.speed - 0.5, c4,
                  self.level.ghost_points),
            Ghost(g_spawn4, "clyde", self.player.speed - 0.5, c3,
                  self.level.ghost_points)
        ]

    @property
    def lives(self) -> int:
        return self.player.lives

    def _update(self, dt: float) -> None:
        """Update game logic, entity positions, and collisions."""
        self.wave_timer -= dt
        self.level.update(dt)
        self.player.update(dt, self.level)
        if self.frightened_timer > 0:
            self.frightened_timer -= dt
            if self.frightened_timer <= 0:
                for gh in self.ghosts:
                    if gh.state == GhostState.FRIGHTENED:
                        gh.state = self.global_state
        if self.wave_timer <= 0:
            if self.global_state == GhostState.SCATTER:
                self.global_state = GhostState.CHASE
                self.wave_timer = 15.0
            else:
                self.global_state = GhostState.SCATTER
                self.wave_timer = 7.0
            for gh in self.ghosts:
                if (gh.state == GhostState.FRIGHTENED
                        or gh.state == GhostState.EATEN):
                    continue
                gh.state = self.global_state
        for gh in self.ghosts:
            gh.update(dt, self.level, self.player)
            if gh.cell == self.player.cell and gh.state != GhostState.EATEN:
                if gh.state == GhostState.FRIGHTENED:
                    gh.state = GhostState.EATEN
                    self.score += gh.points
                else:
                    if not self.player.is_invincible:
                        self.player.lives -= 1
                        self.player.reset_state()
                        self.player.cell = self.level.player_spawn
                        for fa in self.ghosts:
                            fa.reset_state()
                            fa.cell = fa.spawn_pos
        for item in self.level.collectibles[:]:
            if item.cell == self.player.cell:
                self.score += item.points
                self.level.collectibles.remove(item)
                if item.sprite_id == "superpacgum":
                    self.frightened_timer = 8.0
                    for gh in self.ghosts:
                        gh.state = GhostState.FRIGHTENED
        if (self.level.is_completed() or self.level.time_left <= 0
                or self.player.lives <= 0):
            self.is_running = False

    def run(self) -> None:
        """The main Game Loop."""
        while self.is_running:
            self._update(0.016)
        print("Game Finished!")
        print(f"Finally score: {self.score}")
