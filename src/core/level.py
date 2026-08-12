from src.states import Direction


class Level:
    """Represents a single maze level: the grid and its walls.

    Attributes:
        grid: 2D grid of cell values (row-major), int-typed to allow
            multiple cell kinds in the future (wall, path, tunnel...).
    """

    _WALL_MASKS = {
        Direction.UP: 1,
        Direction.RIGHT: 2,
        Direction.DOWN: 4,
        Direction.LEFT: 8
    }

    def __init__(self, grid: list[list[int]]) -> None:
        self.grid = grid
        ...

    def is_blocked(self, cell: tuple[int, int], direction: Direction) -> bool:
        """Return whether the given (col, row) cell blocks movement."""
        cell_value = self.grid[cell[1]][cell[0]]
        wall_flag = self._WALL_MASKS[direction]
        return (cell_value & wall_flag) != 0
