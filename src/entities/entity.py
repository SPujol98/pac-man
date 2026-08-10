from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING
from src.states import Direction

if TYPE_CHECKING:
    from src.core.level import Level


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
    def update(self, dt: float, level: "Level") -> None:
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
    def _choose_direction(self, level: "Level") -> Optional[Direction]:
        """Decide the next direction. Implemented by each subclass."""
        ...

    def update(self, dt: float, level: "Level") -> None:
        if self.direction is None:
            # Intentamos arrancar si estábamos parados
            self.direction = self._choose_direction(level)
            if self.direction is None:
                return

        # Avanzamos un porcentaje de la celda basado en la velocidad y el tiemp
        self.progress += self.speed * dt

        # Si llegamos a 1.0, hemos cruzado al centro de la siguiente celda
        if self.progress >= 1.0:
            self.cell = (self.cell[0] + self.direction.dx,
                         self.cell[1] + self.direction.dy)

            # Preguntamos hacia dónde ir ahora
            next_dir = self._choose_direction(level)

            if next_dir is None:
                # Si hay un muro, paramos en seco y nos clavamos en la celda
                self.direction = None
                self.progress = 0.0
            else:
                # Si podemos seguir, guardamos la nueva dirección y
                # conservamos el exceso de progreso para no perder fluidez
                self.direction = next_dir
                self.progress -= 1.0


class Collectible(Entity):
    """Base class for items the player can eat for points.

    Attributes:
        points: Score value awarded when eaten.
    """
    def __init__(self, cell: tuple[int, int], sprite_id: str,
                 points: int) -> None:
        super().__init__(cell, sprite_id)
        self.points = points

    def update(self, dt: float, level: "Level") -> None:
        """Collectibles are static; nothing to update per frame."""
        pass
