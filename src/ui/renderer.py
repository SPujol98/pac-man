from typing import Dict, List, Optional, Tuple
import pygame

from src.states import Direction, GhostState
from src.entities.player import Player
from src.entities.ghost import Ghost
from src.entities.entity import Collectible
from src.ui import sprites

import math


class Renderer:
    """Render the maze grid, items, Pac-Man, and ghosts in neon style."""

    SPRITE_KEYS: Dict[GhostState, str] = {
        GhostState.EATEN: "eaten",
        GhostState.FRIGHTENED: "frightened",
    }

    COLOR_WALL_CORE = (0, 229, 255)
    COLOR_PACGUM = (255, 184, 222)
    COLOR_SUPER_PACGUM = (255, 64, 200)
    COLOR_SUPER_HALO = (120, 0, 90)
    COLOR_PACMAN = (255, 255, 0)

    GHOST_COLORS: Dict[str, Tuple[int, int, int]] = {
        "blinky": (255, 0, 0),
        "pinky": (255, 184, 255),
        "inky": (0, 255, 255),
        "clyde": (255, 184, 82),
        "frightened": (33, 33, 255),
    }

    ROTATIONS: Dict[Direction, int] = {
        Direction.RIGHT: 0,
        Direction.LEFT: 180,
        Direction.UP: 90,
        Direction.DOWN: 270,
    }

    GLOW_PASSES: Tuple[Tuple[int, int], ...] = (
        (9, 40),
        (6, 80),
        (3, 130),
        (1, 255),
    )

    def __init__(self, screen_width: int, screen_height: int) -> None:
        self.width = screen_width
        self.height = screen_height
        self._maze_cache: Optional[pygame.Surface] = None
        self._maze_cache_key: Optional[Tuple[int, int, int, int]] = None

    def load_sprites_for_tile_size(self, tile_size: int) -> None:
        """Warm the sprite cache for the active tile size."""
        for key in sprites.SPRITE_FILES:
            sprites.try_get_sprite(key, tile_size)
        sprites.try_get_pacman_frames(tile_size)

    def get_layout(self, cols: int, rows: int) -> Tuple[int, int, int]:
        """Calculate the ideal cell size and margins to center the map."""
        tile_size = min(self.width // cols, (self.height - 40) // rows)
        off_x = (self.width - (cols * tile_size)) // 2
        off_y = ((self.height - 40 - (rows * tile_size)) // 2) + 40
        return tile_size, off_x, off_y

    def _neon_line(self, surface: pygame.Surface,
                   start: Tuple[int, int],
                   end: Tuple[int, int]) -> None:
        """Draw a glowing line through stepped alpha passes."""
        for width, alpha in self.GLOW_PASSES:
            color = (*self.COLOR_WALL_CORE, alpha)
            pygame.draw.line(surface, color, start, end, width)

    def _neon_rect(self, surface: pygame.Surface,
                   rect: pygame.Rect) -> None:
        """Draw a glowing rounded-rect outline through alpha passes."""
        for width, alpha in self.GLOW_PASSES:
            color = (*self.COLOR_WALL_CORE, alpha)
            pygame.draw.rect(surface, color, rect,
                             width=width, border_radius=4)

    def _build_maze_surface(self, grid: List[List[int]], tile_size: int,
                            off_x: int, off_y: int) -> pygame.Surface:
        """Pre-render the whole maze once with its glow onto one surface."""
        maze = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 1

        for r in range(rows):
            for c in range(cols):
                val = grid[r][c]
                x = off_x + (c * tile_size)
                y = off_y + (r * tile_size)

                if val == 15:
                    rect = pygame.Rect(x + 2, y + 2,
                                       tile_size - 4, tile_size - 4)
                    self._neon_rect(maze, rect)

                elif val > 0:
                    if val & 1:
                        self._neon_line(maze, (x, y), (x + tile_size, y))

                    if val & 2:
                        self._neon_line(maze, (x + tile_size, y),
                                        (x + tile_size, y + tile_size))

                    if val & 4:
                        self._neon_line(maze, (x, y + tile_size),
                                        (x + tile_size, y + tile_size))

                    if val & 8:
                        self._neon_line(maze, (x, y), (x, y + tile_size))

        return maze

    def draw_maze(
        self,
        surface: pygame.Surface,
        grid: List[List[int]],
        tile_size: int,
        off_x: int,
        off_y: int
    ) -> None:
        """Draw the neon maze, reusing the cached pre-rendered surface."""
        cache_key = (id(grid), tile_size, off_x, off_y)
        if self._maze_cache is None or self._maze_cache_key != cache_key:
            self._maze_cache = self._build_maze_surface(
                grid, tile_size, off_x, off_y)
            self._maze_cache_key = cache_key
        surface.blit(self._maze_cache, (0, 0))

    def draw_collectibles(
            self, surface: pygame.Surface, collectibles: List[Collectible],
            tile_size: int, off_x: int, off_y: int) -> None:
        """Draw pulsing pacgums and blinking, glowing superpacgums."""
        ticks = pygame.time.get_ticks()
        pulse = (math.sin(ticks * 0.006) + 1) / 2

        for item in collectibles:
            cx, cy = item.cell
            center_x = off_x + (cx * tile_size) + (tile_size // 2)
            center_y = off_y + (cy * tile_size) + (tile_size // 2)

            if item.sprite_id == "superpacgum":
                if (ticks // 250) % 2 == 0:
                    radius = max(4, tile_size // 4)
                    pygame.draw.circle(
                        surface, self.COLOR_SUPER_HALO,
                        (center_x, center_y), radius + 3)
                    pygame.draw.circle(
                        surface, self.COLOR_SUPER_PACGUM,
                        (center_x, center_y), radius)
            else:
                radius = max(2, tile_size // 8) + int(pulse * 1.5)
                pygame.draw.circle(
                    surface, self.COLOR_PACGUM,
                    (center_x, center_y), radius)

    def draw_player(self, surface: pygame.Surface, player: Player,
                    tile_size: int, off_x: int, off_y: int) -> None:
        """Draw Pac-Man with animated chomp frames, interpolated."""
        px, py = float(player.cell[0]), float(player.cell[1])
        if player.direction is not None:
            px += player.direction.dx * player.progress
            py += player.direction.dy * player.progress

        screen_x = int(off_x + (px * tile_size))
        screen_y = int(off_y + (py * tile_size))

        frames = sprites.try_get_pacman_frames(tile_size)
        if frames is not None:
            if player.direction is None:
                frame = frames[1]
            else:
                sequence = (0, 1, 2, 1)
                index = sequence[(pygame.time.get_ticks() // 90) % 4]
                frame = frames[index]
            angle = self.ROTATIONS.get(player.direction or
                                       player.facing_direction, 0)
            rotated = pygame.transform.rotate(frame, angle)
            surface.blit(rotated, (screen_x, screen_y))
        else:
            center = (screen_x + tile_size // 2, screen_y + tile_size // 2)
            pygame.draw.circle(
                surface, self.COLOR_PACMAN,
                center, max(4, tile_size // 2 - 2))

    def _ghost_sprite(self, ghost: Ghost, tile_size: int,
                      frightened_timer: Optional[float]
                      ) -> Optional[pygame.Surface]:
        """Resolve the sprite for a ghost, handling the white flash."""
        if ghost.state == GhostState.EATEN:
            return sprites.try_get_sprite("eaten", tile_size)

        if ghost.state == GhostState.FRIGHTENED:
            flashing = (
                frightened_timer is not None
                and frightened_timer < 2.0
                and (pygame.time.get_ticks() // 150) % 2 == 0
            )
            if flashing:
                return sprites.get_white_sprite_opt("frightened", tile_size)
            return sprites.try_get_sprite("frightened", tile_size)

        return sprites.try_get_sprite(ghost.ghost_type.lower(), tile_size)

    def draw_ghosts(self, surface: pygame.Surface, ghosts: List[Ghost],
                    tile_size: int, off_x: int, off_y: int,
                    frightened_timer: Optional[float] = None) -> None:
        """Draw the ghosts with smooth animation between cells."""
        for ghost in ghosts:
            gx, gy = float(ghost.cell[0]), float(ghost.cell[1])
            if ghost.direction is not None:
                gx += ghost.direction.dx * ghost.progress
                gy += ghost.direction.dy * ghost.progress

            screen_x = int(off_x + (gx * tile_size))
            screen_y = int(off_y + (gy * tile_size))

            sprite = self._ghost_sprite(ghost, tile_size, frightened_timer)
            if sprite is not None:
                surface.blit(sprite, (screen_x, screen_y))
            else:

                if ghost.state == GhostState.EATEN:
                    eye_y = screen_y + tile_size // 2
                    eye_r = max(2, tile_size // 6)

                    pygame.draw.circle(surface, (255, 255, 255),
                                       (screen_x + tile_size // 3, eye_y),
                                       eye_r)
                    pygame.draw.circle(surface, (255, 255, 255),
                                       (screen_x + 2 * tile_size // 3, eye_y),
                                       eye_r)

                    pupil_r = max(1, eye_r // 2)
                    pygame.draw.circle(surface, (0, 0, 255),
                                       (screen_x + tile_size // 3, eye_y),
                                       pupil_r)
                    pygame.draw.circle(surface, (0, 0, 255),
                                       (screen_x + 2 * tile_size // 3, eye_y),
                                       pupil_r)

                else:
                    color = (
                        (255, 255, 255)
                        if (ghost.state == GhostState.FRIGHTENED
                            and frightened_timer is not None
                            and frightened_timer < 2.0
                            and (pygame.time.get_ticks() // 150) % 2 == 0)
                        else self.GHOST_COLORS.get(
                            "frightened"
                            if ghost.state == GhostState.FRIGHTENED
                            else ghost.ghost_type,
                            (255, 0, 0))
                    )
                    head_center = (screen_x + tile_size // 2,
                                   screen_y + tile_size // 3)
                    pygame.draw.circle(surface, color,
                                       head_center,
                                       tile_size // 3)
                    pygame.draw.rect(
                        surface,
                        color,
                        (screen_x + 2,
                         screen_y + tile_size // 3,
                         tile_size - 4, tile_size // 2)
                        )

                    eye_y = screen_y + tile_size // 3
                    eye_r = max(1, tile_size // 8)
                    pygame.draw.circle(surface, (255, 255, 255),
                                       (screen_x + tile_size // 3, eye_y),
                                       eye_r)
                    pygame.draw.circle(surface, (255, 255, 255),
                                       (screen_x + 2 * tile_size // 3, eye_y),
                                       eye_r)
