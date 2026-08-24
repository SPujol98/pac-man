import sys

from dataclasses import dataclass
from typing import List, Tuple

try:
    import mazegenerator
except ImportError:
    print("[FATAL] The mazegenerator could not be imported.")
    sys.exit(0)


WALL_NORTH = 1
WALL_EAST = 2
WALL_SOUTH = 4
WALL_WEST = 8


@dataclass(frozen=True)
class MazeData:
    """Immutable processed maze handed to the game engine."""

    grid: List[List[int]]
    width: int
    height: int
    entry: Tuple[int, int]
    exit: Tuple[int, int]


def is_wall_present(cell_value: int, wall_flag: int) -> bool:
    """Return whether a cell's bitmask declares a wall in a direction."""
    return (cell_value & wall_flag) != 0


def load_maze(
    width: int = 21,
    height: int = 21,
    seed: int = 42,
) -> MazeData:
    """Generate a maze via the external package, clamping dimensions."""
    try:
        safe_w = min(max(5, int(width)), 45)
        safe_h = min(max(5, int(height)), 45)
        safe_seed = int(seed)
    except (ValueError, TypeError):
        raise ValueError("[Warning] Invalid arguments in load_maze.")

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
            print("[Warning] MazeGenerator returned an invalid/empty grid.")

        return MazeData(
            grid=raw_maze,
            width=safe_w,
            height=safe_h,
            entry=generator.maze_entry,
            exit=generator.maze_exit,
        )
    except Exception:
        raise ValueError("[Warning] Internal error in MazeGenerator.")
