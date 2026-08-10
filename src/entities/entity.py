from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING
from src.states import Direction

if TYPE_CHECKING:
    from src.core.level import Level


class Entity(ABC):
    """Abstract base class for anything that occupies a cell on the map.

    Subclasses must implement `update` to define per-frame behavior.

    Attributes:
        cell: Grid position (column, row)
        px/py: Horizontal/vertical pixel for rendering.
        sprite_id: Identifier of the sprite to render.
    """
    def __init__(self, cell: tuple[int, int], tile_size: int,
                 sprite_id: str) -> None:
        self.cell = cell
        self.tile_size = tile_size
        self.px, self.py = self._cell_to_pixels(cell)
        self.sprite_id = sprite_id

    @abstractmethod
    def update(self, dt: float, level: "Level") -> None:
        """The entity's state advances by one frame."""
        ...

    def _cell_to_pixels(self, cell: tuple[int, int]) -> tuple[float, float]:
        px: float = cell[0] * self.tile_size
        py: float = cell[1] * self.tile_size
        return px, py


class MovingEntity(Entity):
    """Base class for entities that moves in the grid.

    Subclasses must implement _choose_direction to decide movement.

    Attributes:
        speed: Movement speed in pixels per second.
        direction: Current facing direction, or None if not moving yet.
    """
    def __init__(self, cell: tuple[int, int], tile_size: int, sprite_id: str,
                 speed: float, direction: Optional[Direction] = None) -> None:
        super().__init__(cell, tile_size, sprite_id)
        self.speed = speed
        self.direction = direction

    @abstractmethod
    def _choose_direction(self, level: "Level") -> Optional[Direction]:
        """Decide the next direction. Implemented by each subclass."""
        ...

    def update(self, dt: float, level: "Level") -> None:
        if self.direction is None:
            return
        target_cell: tuple[int, int] = (self.cell[0] + self.direction.dx,
                                        self.cell[1] + self.direction.dy)
        target_px, target_py = self._cell_to_pixels(target_cell)
        remaining_px = abs(target_px - self.px)
        remaining_py = abs(target_py - self.py)
        remaining_distance = remaining_px + remaining_py
        frame_progress = self.speed * dt
        if frame_progress >= remaining_distance:
            self.px, self.py = target_px, target_py
            self.cell = target_cell
            self.direction = self._choose_direction(level)
        else:
            self.px += self.direction.dx * self.speed * dt
            self.py += self.direction.dy * self.speed * dt


class Collectible(Entity):
    """Base class for items the player can eat for points.

    Attributes:
        points: Score value awarded when eaten.
    """
    def __init__(self, cell: tuple[int, int], tile_size: int,
                 sprite_id: str, points: int) -> None:
        super().__init__(cell, tile_size, sprite_id)
        self.points = points

    def update(self, dt: float, level: "Level") -> None:
        """Collectibles are static; nothing to update per frame."""
        pass
