from __future__ import annotations
from src.entities.entity import MovingEntity
from src.states import Direction, GhostState
from typing import Optional, TYPE_CHECKING

import random


if TYPE_CHECKING:
    from src.core.level import Level
    from src.entities.player import Player


class Ghost(MovingEntity):
    """Base class for enemy ghosts.

    Attributes:
        state: Current AI behavior state.
    """
    def __init__(self, cell: tuple[int, int], ghost_type: str, speed: float,
                 scatter_corner: tuple[int, int],
                 points: int,
                 direction: Optional[Direction] = None):
        super().__init__(cell, ghost_type, speed, direction)
        self.ghost_type = ghost_type
        self.state: GhostState = GhostState.SCATTER
        self.scatter_corner = scatter_corner
        self.points = points
        self.spawn_pos = cell
        self.respawn_timer: float = 7.0

    def _choose_direction(
            self, level: Level,
            player: Optional["Player"] = None) -> Optional[Direction]:
        match self.state:
            case GhostState.SCATTER:
                return self._get_best_turn(level, self.scatter_corner)
            case GhostState.CHASE:
                if player is None:
                    return self._get_best_turn(level, self.scatter_corner)
                return self._get_best_turn(
                    level, self._get_chase_target(level, player))
            case GhostState.FRIGHTENED:
                val_dir: list[Direction] = [
                    d for d in Direction
                    if not level.is_blocked(self.cell, d)
                    and (self.direction is None
                         or d != self.direction.opposite())]
                return random.choice(val_dir) if val_dir else (
                    self.direction.opposite() if self.direction
                    else Direction.RIGHT
                )
            case GhostState.EATEN:
                return self._get_best_turn(level, self.spawn_pos)
        return None

    def _get_best_turn(self, level: Level,
                       target_cell: tuple[int, int]) -> Direction:
        best_dir: Optional[Direction] = None
        min_dist_sq: float = float("inf")
        for d in Direction:
            if self.direction is not None and d == self.direction.opposite():
                continue
            if level.is_blocked(self.cell, d):
                continue
            next_cell = (self.cell[0] + d.dx, self.cell[1] + d.dy)
            dist_sq = ((next_cell[0] - target_cell[0]) ** 2 +
                       (next_cell[1] - target_cell[1]) ** 2)
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                best_dir = d
        return (best_dir if best_dir is not None else
                (self.direction.opposite() if self.direction else
                 Direction.RIGHT))

    def _get_chase_target(self, level: Level,
                          player: Player) -> tuple[int, int]:
        """Calculate the target cell during CHASE mode.
        Needs to be overwrite by the specific subclass of every ghost.
        """
        match self.ghost_type:
            case "blinky":
                return player.cell
            case "pinky":
                if player.direction is None:
                    return player.cell
                return (player.cell[0] + player.direction.dx * 4,
                        player.cell[1] + player.direction.dy * 4)
            case "inky":
                if player.direction is None:
                    return player.cell
                return (player.cell[0] + player.direction.dx * 2,
                        player.cell[1] + player.direction.dy * 2)
            case "clyde":
                dist_sq = ((self.cell[0] - player.cell[0]) ** 2 +
                           (self.cell[1] - player.cell[1]) ** 2)
                if dist_sq > 64:
                    return player.cell
                return self.scatter_corner
            case _:
                return player.cell

    def get_current_speed(self, player: Optional["Player"] = None):
        match self.state:
            case GhostState.CHASE:
                return self.speed
            case GhostState.FRIGHTENED:
                if player is not None:
                    return player.speed * (2/3)
                return 2.0
            case GhostState.SCATTER:
                return self.speed
            case GhostState.EATEN:
                return self.speed * 2

    def update(self, dt: float, level: "Level",
               player: Optional["Player"] = None):
        super().update(dt, level, player)
        if self.state == GhostState.EATEN:
            self.respawn_timer -= dt
            if self.respawn_timer <= 0.0 and self.cell == self.spawn_pos:
                self.state = GhostState.SCATTER
                self.respawn_timer = 7.0
