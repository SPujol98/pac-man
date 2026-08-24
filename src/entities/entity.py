from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING
from src.states import Direction

if TYPE_CHECKING:
    from src.core.level import Level
    from src.entities.player import Player


class Entity(ABC):
    """Abstract base class for anything that occupies a cell on the map."""

    def __init__(self, cell: tuple[int, int], sprite_id: str) -> None:
        self.cell = cell
        self.sprite_id = sprite_id

    @abstractmethod
    def update(self, dt: float, level: "Level",
               player: Optional["Player"] = None) -> None:
        """Advance the entity's state by one frame."""
        ...


class MovingEntity(Entity):
    """Base class for entities that move through the grid."""

    def __init__(self, cell: tuple[int, int], sprite_id: str,
                 speed: float, direction: Optional[Direction] = None) -> None:
        super().__init__(cell, sprite_id)
        self.speed = speed
        self.direction = direction
        self.progress: float = 0.0

    @abstractmethod
    def _choose_direction(self, level: "Level",
                          player: Optional["Player"]) -> Optional[Direction]:
        """Decide the next direction, implemented by each subclass."""
        ...

    def update(self, dt: float, level: "Level",
               player: Optional["Player"] = None) -> None:
        if self.direction is None:
            self.direction = self._choose_direction(level, player)
            if self.direction is None:
                return

        self.progress += self.get_current_speed(player) * dt

        if self.progress >= 1.0:
            self.cell = (self.cell[0] + self.direction.dx,
                         self.cell[1] + self.direction.dy)

            next_dir = self._choose_direction(level, player)

            if next_dir is None:
                self.direction = None
                self.progress = 0.0
            else:

                self.direction = next_dir
                self.progress -= 1.0

    def get_current_speed(self, player: Optional["Player"] = None) -> float:
        """Return the effective speed for this frame (overridable)."""
        return self.speed

    def reset_state(self) -> None:
        """Reposition the entity at its current cell, stopped."""
        self.progress = 0.0
        self.direction = None


class Collectible(Entity):
    """Base class for static items the player can eat for points."""

    def __init__(self, cell: tuple[int, int], sprite_id: str,
                 points: int) -> None:
        super().__init__(cell, sprite_id)
        self.points = points

    def update(self, dt: float, level: "Level",
               player: Optional["Player"] = None) -> None:
        """Collectibles are static; nothing to update per frame."""
        pass
