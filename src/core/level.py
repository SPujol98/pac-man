from __future__ import annotations
from typing import TYPE_CHECKING
from src.states import Direction
from src.entities.collectibles import Pacgum, SuperPacgum

if TYPE_CHECKING:
    from src.entities.entity import Collectible


class Level:
    """Represents a single maze level: the grid and its walls.

    Attributes:
        grid: 2D grid of cell values (row-major), int-typed to allow
            multiple cell kinds in the future (wall, path, tunnel...).
        time_left: The remaining time to complete the level.
        collectibles: List of all active pacgums and superpacgums.
        player_spawn: The (x, y) starting coordinate for the player.
        ghost_spawns: List of (x, y) starting coordinates for the ghosts.
        superpacgum_spawns: List of (x, y) coordinates for superpacgums.
    """

    _WALL_MASKS = {
        Direction.UP: 1,
        Direction.RIGHT: 2,
        Direction.DOWN: 4,
        Direction.LEFT: 8
    }

    def __init__(self, grid: list[list[int]],
                 pacgum_points: int,
                 superpacgum_points: int,
                 ghost_points: int,
                 time_left: float = 90.0) -> None:
        self.grid = grid
        self.ghost_points = ghost_points
        self.time_left = time_left
        self.collectibles: list[Collectible] = []
        self.player_spawn: tuple[int, int] = (0, 0)
        self.ghost_spawns: list[tuple[int, int]] = []
        self.superpacgum_spawns: list[tuple[int, int]] = []

        self._find_spawn_points()
        self._spawn_collectibles(pacgum_points, superpacgum_points)

    def is_blocked(self, cell: tuple[int, int], direction: Direction) -> bool:
        """Return whether the given (col, row) cell blocks movement."""
        cell_value = self.grid[cell[1]][cell[0]]
        wall_flag = self._WALL_MASKS[direction]
        return (cell_value & wall_flag) != 0

    def update(self, dt: float) -> None:
        """Advance the level timer."""
        self.time_left = max(0.0, self.time_left - dt)

    def is_completed(self) -> bool:
        """Return True if all collectibles have been eaten."""
        return len(self.collectibles) == 0

    def _get_closest_walkable_cell(self, target_x: int,
                                   target_y: int) -> tuple[int, int]:
        """Find and return the nearest walkable cell to the given coordinates.
        """
        best_cell: tuple[int, int] = (0, 0)
        min_dist_sq: float = float("inf")

        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                if self.grid[y][x] == 15:
                    continue
                dist_sq = (x - target_x) ** 2 + (y - target_y) ** 2
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    best_cell = (x, y)
        return best_cell

    def _find_spawn_points(self) -> None:
        """Calculate and assign the spawn coordinates for the player (mid),
        superpacgums (corners), and ghosts (adjacent to corners).
        """
        if not self.grid or not self.grid[0]:
            return

        max_y = len(self.grid) - 1
        max_x = len(self.grid[0]) - 1

        self.player_spawn = self._get_closest_walkable_cell(
            max_x // 2, max_y // 2)

        self.superpacgum_spawns = [
            self._get_closest_walkable_cell(0, 0),
            self._get_closest_walkable_cell(max_x, 0),
            self._get_closest_walkable_cell(0, max_y),
            self._get_closest_walkable_cell(max_x, max_y)
        ]

        for sx, sy in self.superpacgum_spawns:
            for dx, dy in [(1,  0), (-1, 0), (0, 1), (0, -1)]:
                nx = sx + dx
                ny = sy + dy
                if 0 <= nx <= max_x and 0 <= ny <= max_y:
                    if self.grid[ny][nx] != 15:
                        self.ghost_spawns.append((nx, ny))
                        break

    def _spawn_collectibles(self, pacgum_points: int,
                            superpacgum_points: int) -> None:
        """Scan the grid and populate paths with pacgums and
        corners with superpacgums.
        """
        for pos in self.superpacgum_spawns:
            self.collectibles.append(SuperPacgum(pos, superpacgum_points))

        blacklist = ([self.player_spawn] + self.superpacgum_spawns +
                     self.ghost_spawns)
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                if self.grid[y][x] == 15:
                    continue
                if (x, y) not in blacklist:
                    self.collectibles.append(Pacgum((x, y), pacgum_points))
