from abc import ABC, abstractmethod
from typing import Optional
from src.states import Direction


class Entity(ABC):
    """Base class, contains the interpolation pixel logic
    and is the comun contract.

    Abstract class that contains the update method using the dt: delta time.

    Attributes:
        cell: Grid position (column, row)
        px/py: Horizontal/vertical pixel for rendering.
        sprite_id: Identifier of the spirte to render.
    """
    def __init__(self, cell: tuple[int, int], tile_size: int,
                 sprite_id: str) -> None:
        self.cell = cell
        self.tile_size = tile_size
        self.px, self.py = self._cell_to_pixels(cell)
        self.sprite_id = sprite_id

    @abstractmethod
    def update(self, dt: float) -> None:
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
    def _choose_direction(self) -> Optional[Direction]:
        """Decide the next direction. Implemented by each subclass."""
        ...

    def update(self, dt: float) -> None:
        ...


class Collectible(Entity):
    pass
