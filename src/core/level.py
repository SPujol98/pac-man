from __future__ import annotations

import random

from typing import TYPE_CHECKING
from src.states import Direction
from src.entities.collectibles import Pacgum, SuperPacgum

if TYPE_CHECKING:
    from src.entities.entity import Collectible


class Level:
    """A single maze level: grid, spawns, collectibles, and timer."""

    _WALL_MASKS = {
        Direction.UP: 1,
        Direction.RIGHT: 2,
        Direction.DOWN: 4,
        Direction.LEFT: 8
    }

    def __init__(self, grid: list[list[int]],
                 pacgum_quantity: int,
                 pacgum_points: int,
                 superpacgum_points: int,
                 ghost_points: int,
                 time_left: float = 90.0) -> None:
        """Initialize the grid, spawn points, and collectibles."""
        self.grid = grid
        self.pacgum_quantity = pacgum_quantity
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

    def force_complete(self) -> None:
        """Clear all remaining collectibles to forcefully end the level."""
        self.collectibles.clear()

    def _get_closest_walkable_cell(self, target_x: int,
                                   target_y: int) -> tuple[int, int]:
        """Return the nearest non-wall cell to the given coordinates."""
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
        """Assign spawns: player (mid), superpacgums (corners), ghosts."""
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
        """Populate paths with pacgums and corners with superpacgums."""
        for pos in self.superpacgum_spawns:
            self.collectibles.append(SuperPacgum(pos, superpacgum_points))

        blacklist = ([self.player_spawn] + self.superpacgum_spawns +
                     self.ghost_spawns)
        available_positions: list[tuple[int, int]] = []
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                if self.grid[y][x] == 15:
                    continue
                if (x, y) not in blacklist:
                    available_positions.append((x, y))
        safe_quantity = min(self.pacgum_quantity, len(available_positions))
        chosen_positions = random.sample(available_positions, safe_quantity)
        for pos in chosen_positions:
            self.collectibles.append(Pacgum(pos, pacgum_points))
