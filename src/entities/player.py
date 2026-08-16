from __future__ import annotations
from src.entities.entity import MovingEntity
from src.states import Direction
from typing import Optional, TYPE_CHECKING


if TYPE_CHECKING:
    from src.core.level import Level


class Player(MovingEntity):
    """The user-controlled character, moved via buffered directional input.

    Attributes:
        lives: Remaining lives before game over.
    """
    def __init__(self, cell: tuple[int, int], speed: float,
                 lives: int) -> None:
        super().__init__(cell, "player", speed)
        self.lives = lives
        self._buffered_direction: Optional[Direction] = None
        self.facing_direction = Direction.RIGHT
        self.is_invincible: bool = False

    def set_desired_direction(self, direction: Direction) -> None:
        self._buffered_direction = direction

    def _choose_direction(
            self, level: Level,
            player: Optional["Player"] = None) -> Optional[Direction]:
        if (self._buffered_direction is not None and
                not level.is_blocked(self.cell, self._buffered_direction)):
            chosen = self._buffered_direction
            self._buffered_direction = None
            self.facing_direction = chosen
            return chosen
        elif (self.direction is not None and
                not level.is_blocked(self.cell, self.direction)):
            self.facing_direction = self.direction
            return self.direction
        return None

    def reset_state(self) -> None:
        super().reset_state()
        self._buffered_direction = None

    def invincible_switch(self) -> None:
        self.is_invincible = not self.is_invincible
