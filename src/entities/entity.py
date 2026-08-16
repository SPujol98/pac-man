from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING
from src.states import Direction

if TYPE_CHECKING:
    from src.core.level import Level
    from src.entities.player import Player


class Entity(ABC):
    """Abstract base class for anything that occupies a cell on the map.

    Subclasses must implement `update` to define per-frame behavior.

    Attributes:
        cell: Grid position (column, row).
        sprite_id: Identifier of the sprite to render.
    """
    def __init__(self, cell: tuple[int, int], sprite_id: str) -> None:
        self.cell = cell
        self.sprite_id = sprite_id

    @abstractmethod
    def update(self, dt: float, level: "Level",
               player: Optional["Player"] = None) -> None:
        """The entity's state advances by one frame."""
        ...


class MovingEntity(Entity):
    """Base class for entities that moves in the grid.

    Subclasses must implement _choose_direction to decide movement.

    Attributes:
        speed: Movement speed in grid cells per second.
        direction: Current facing direction, or None if not moving yet.
        progress: Float from 0.0 to 1.0 representing distance to next cell.
    """
    def __init__(self, cell: tuple[int, int], sprite_id: str,
                 speed: float, direction: Optional[Direction] = None) -> None:
        super().__init__(cell, sprite_id)
        self.speed = speed
        self.direction = direction
        self.progress: float = 0.0

    @abstractmethod
    def _choose_direction(self, level: "Level",
                          player: Optional["Player"]) -> Optional[Direction]:
        """Decide the next direction. Implemented by each subclass."""
        ...

    def update(self, dt: float, level: "Level",
               player: Optional["Player"] = None) -> None:
        if self.direction is None:
            # Attempt to start moving if we were stationary
            self.direction = self._choose_direction(level, player)
            if self.direction is None:
                return

        # Advance a percentage of the cell based on speed and time
        self.progress += self.get_current_speed(player) * dt

        # If we reach 1.0, we have crossed to the center of the next cell
        if self.progress >= 1.0:
            self.cell = (self.cell[0] + self.direction.dx,
                         self.cell[1] + self.direction.dy)

            # Determine where to go next
            next_dir = self._choose_direction(level, player)

            if next_dir is None:
                # If there is a wall, stop completely and stay in the cell
                self.direction = None
                self.progress = 0.0
            else:
                # If we can continue, save the new direction and
                # retain the excess progress to maintain smooth movement
                self.direction = next_dir
                self.progress -= 1.0

    def get_current_speed(self, player: Optional["Player"] = None) -> float:
        return self.speed

    def reset_state(self) -> None:
        self.progress = 0.0
        self.direction = None


class Collectible(Entity):
    """Base class for items the player can eat for points.

    Attributes:
        points: Score value awarded when eaten.
    """
    def __init__(self, cell: tuple[int, int], sprite_id: str,
                 points: int) -> None:
        super().__init__(cell, sprite_id)
        self.points = points

    def update(self, dt: float, level: "Level",
               player: Optional["Player"] = None) -> None:
        """Collectibles are static; nothing to update per frame."""
        pass
