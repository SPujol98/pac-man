from __future__ import annotations
from src.entities.player import Player
from src.entities.ghost import (
    BlinkyGhost,
    PinkyGhost,
    InkyGhost,
    ClydeGhost
)
from src.states import GhostState
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.core.level import Level


class Game:
    """Game controller orchestrating entities, collisions, and score."""

    def __init__(self, level: Level, lives: int,
                 score: Optional[int] = 0) -> None:
        self.level = level
        self.is_running: bool = True
        self.score: int = score if score is not None else 0
        self.wave_timer: float = 7.0
        self.frightened_timer: float = 0.0
        self.global_state: GhostState = GhostState.SCATTER

        self.player = Player(self.level.player_spawn, 5.0, lives)
        g_spawn1, g_spawn2, g_spawn3, g_spawn4 = self.level.ghost_spawns
        c1, c2, c3, c4 = self.level.superpacgum_spawns
        self.ghosts = [
            BlinkyGhost(g_spawn1, self.player.speed - 1, c2,
                        self.level.ghost_points),
            PinkyGhost(g_spawn2, self.player.speed - 1, c1,
                       self.level.ghost_points),
            InkyGhost(g_spawn3, self.player.speed - 1, c4,
                      self.level.ghost_points),
            ClydeGhost(g_spawn4, self.player.speed - 1, c3,
                       self.level.ghost_points)
        ]

    @property
    def lives(self) -> int:
        return self.player.lives

    def update(self, dt: float) -> None:
        """Advance the simulation by one frame."""
        self.wave_timer -= dt
        self.level.update(dt)
        self.player.update(dt, self.level)

        self._update_frightened(dt)
        self._update_wave()
        self._update_ghosts(dt)
        self._eat_collectibles()
        self._check_end_conditions()

    def _update_frightened(self, dt: float) -> None:
        """Count down the frightened window and revert ghosts when it ends."""
        if self.frightened_timer <= 0:
            return
        self.frightened_timer -= dt
        if self.frightened_timer <= 0:
            for gh in self.ghosts:
                if gh.state == GhostState.FRIGHTENED:
                    gh.state = self.global_state

    def _update_wave(self) -> None:
        """Flip the global SCATTER/CHASE wave and sync non-busy ghosts."""
        if self.wave_timer > 0:
            return
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

    def _update_ghosts(self, dt: float) -> None:
        """Move every ghost and resolve player-ghost collisions."""
        for gh in self.ghosts:
            gh.update(dt, self.level, self.player)
            if gh.cell == self.player.cell and gh.state != GhostState.EATEN:
                if gh.state == GhostState.FRIGHTENED:
                    gh.state = GhostState.EATEN
                    self.score += gh.points
                else:
                    if not self.player.is_invincible:
                        self._respawn_after_death()

    def _respawn_after_death(self) -> None:
        """Reset the player and every ghost back to their spawn points."""
        self.player.lives -= 1
        self.player.reset_state()
        self.player.cell = self.level.player_spawn
        for fa in self.ghosts:
            fa.reset_state()
            fa.cell = fa.spawn_pos

    def _eat_collectibles(self) -> None:
        """Award points for eaten items and trigger frightened mode."""
        for item in self.level.collectibles[:]:
            if item.cell == self.player.cell:
                self.score += item.points
                self.level.collectibles.remove(item)
                if item.sprite_id == "superpacgum":
                    self.frightened_timer = 8.0
                    for gh in self.ghosts:
                        if gh.state != GhostState.EATEN:
                            gh.state = GhostState.FRIGHTENED

    def _check_end_conditions(self) -> None:
        """Stop the simulation on victory, timeout, or game over."""
        if (self.level.is_completed() or
                self.level.time_left <= 0 or
                self.player.lives <= 0):
            self.is_running = False
