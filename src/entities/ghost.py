from __future__ import annotations
from src.entities.entity import MovingEntity
from src.states import Direction
from typing import Optional, TYPE_CHECKING
from enum import Enum


if TYPE_CHECKING:
    from src.core.level import Level


class GhostState(Enum):
    SCATTER = 1
    CHASE = 2
    FRIGHTENED = 3
    EATEN = 4


class Ghost(MovingEntity):
    """Base class for enemy ghosts.

    Attributes:
        state: Current AI behavior state.
    """
    def __init__(self, cell: tuple[int, int], ghost_type: str, speed: float,
                 direction: Optional[Direction] = None):
        super().__init__(cell, ghost_type, speed, direction)
        self.state: GhostState = GhostState.SCATTER

    def _choose_direction(self, level: Level) -> Optional[Direction]:
        match self.state:
            case GhostState.SCATTER:
                pass
            case GhostState.CHASE:
                pass
            case GhostState.FRIGHTENED:
                pass
            case GhostState.EATEN:
                pass
        return None

    def _get_best_turn(self, level: Level,
                       target_cell: tuple[int, int]) -> Direction:
        return Direction
