from dataclasses import dataclass
from typing import List, Tuple
try:
    import mazegenerator
    _MAZEGEN_AVAILABLE = True
except ImportError as err:
    print(f"[Warning] The external library could not be imported: {err}. "
          "Fallback maps will be used.")
    _MAZEGEN_AVAILABLE = False

WALL_NORTH = 1
WALL_EAST = 2
WALL_SOUTH = 4
WALL_WEST = 8


@dataclass(frozen=True)
class MazeData:
    """Data structure that passes the processed maze to the game engine.

    Attributes:
        grid: A 2D array of integers where each cell is a bitmask
            representing walls.
        width: Width in cells.
        height: Height in cells.
        entry: Coordinates (col, row) of the entrance.
        exit: Coordinates (col, row) of the exit.
    """

    grid: List[List[int]]
    width: int
    height: int
    entry: Tuple[int, int]
    exit: Tuple[int, int]


def is_wall_present(cell_value: int, wall_flag: int) -> bool:
    """Engine helper: Indicates whether there is a wall in a given direction.

    In MazeGenerator, bits represent walls. If the bit is set (1),
    there is a wall. If a bitwise NOT (~) was applied, the path is open.

    Args:
        cell_value: Integer value of the cell in the grid array.
        wall_flag: WALL_NORTH, WALL_EAST, WALL_SOUTH, or WALL_WEST.

    Returns:
        True if there is a wall in that direction,
        False if the corridor is open.
    """
    return (cell_value & wall_flag) != 0


def _generate_fallback_maze(width: int, height: int) -> MazeData:
    """Generate a safe default map (an empty room with borders)."""
    w = max(5, width)
    h = max(5, height)

    grid = [[0 for _ in range(w)] for _ in range(h)]
    for y in range(h):
        for x in range(w):
            val = 0
            if y == 0:
                val |= WALL_NORTH
            if y == h - 1:
                val |= WALL_SOUTH
            if x == 0:
                val |= WALL_WEST
            if x == w - 1:
                val |= WALL_EAST
            grid[y][x] = val

    return MazeData(
        grid=grid,
        width=w,
        height=h,
        entry=(1, 1),
        exit=(w - 2, h - 2),
    )


def load_maze(
    width: int = 21,
    height: int = 21,
    seed: int = 42,
) -> MazeData:
    """Loads and generates a maze using the external MazeGenerator.

    Sets 'perfect = False' to ensure there are loops in the corridors.
    If the external library fails or cannot be found, it returns a default map.
        Clamp dimensions: min 5 to prevent indexing errors, max 45 to prevent
        DFS RecursionError in the external library
    """
    try:
        safe_w = min(max(5, int(width)), 45)
        safe_h = min(max(5, int(height)), 45)
        safe_seed = int(seed)
    except (ValueError, TypeError):
        print("[Warning] Invalid arguments in load_maze. Using fallback.")
        return _generate_fallback_maze(21, 21)

    if not _MAZEGEN_AVAILABLE:
        return _generate_fallback_maze(safe_w, safe_h)

    try:
        generator = mazegenerator.MazeGenerator(
            size=(safe_w, safe_h),
            perfect=False,
            entry_cell=(0, 0),
            exit_cell=(safe_w - 1, safe_h - 1),
            seed=safe_seed,
        )

        raw_maze = generator.maze

        if (
            not raw_maze or
            len(raw_maze) != safe_h or
            len(raw_maze[0]) != safe_w
        ):
            print("[Warning] MazeGenerator returned an invalid/empty grid. "
                  "Using fallback.")
            return _generate_fallback_maze(safe_w, safe_h)

        return MazeData(
            grid=raw_maze,
            width=safe_w,
            height=safe_h,
            entry=generator.maze_entry,
            exit=generator.maze_exit,
        )

    except Exception as err:
        print(f"[Warning] Internal error in MazeGenerator: {err}. "
              "Using fallback.")
        return _generate_fallback_maze(safe_w, safe_h)
