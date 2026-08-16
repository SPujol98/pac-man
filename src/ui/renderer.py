from pathlib import Path
from typing import Dict, List, Tuple
import pygame

from src.states import Direction, GhostState
from src.entities.player import Player
from src.entities.ghost import Ghost
from src.entities.entity import Collectible


class Renderer:
    """Render the maze grid, items, Pac-Man, and ghosts."""

    def __init__(self, screen_width: int, screen_height: int) -> None:
        self.width = screen_width
        self.height = screen_height

        self.COLOR_WALL = (33, 33, 222)
        self.COLOR_PACGUM = (255, 183, 174)
        self.COLOR_SUPER_PACGUM = (255, 255, 255)
        self.COLOR_PACMAN = (255, 255, 0)

        self.GHOST_COLORS: Dict[str, Tuple[int, int, int]] = {
            "blinky": (255, 0, 0),
            "pinky": (255, 184, 255),
            "inky": (0, 255, 255),
            "clyde": (255, 184, 82),
            "frightened": (33, 33, 255),
        }

        self.ROTATIONS: Dict[Direction, int] = {
            Direction.RIGHT: 0,
            Direction.LEFT: 180,
            Direction.UP: 90,
            Direction.DOWN: 270,
        }

        self.sprites: Dict[str, pygame.Surface] = {}

    def load_sprites_for_tile_size(self, tile_size: int) -> None:
        """Load and scale the sprites if the cell size changes."""
        assets_dir = Path("src/assets/images")
        files = {
            "player": "pacman.png",
            "blinky": "blinky.png",
            "pinky": "pinky.png",
            "inky": "inky.png",
            "clyde": "clyde.png",
            "frightened": "frightened.png",
        }

        for key, filename in files.items():
            path = assets_dir / filename
            if path.is_file():
                try:
                    img = pygame.image.load(str(path)).convert_alpha()
                    self.sprites[key] = (pygame.transform.scale(
                        img, (tile_size, tile_size)))
                except pygame.error:
                    pass

    def get_layout(self, cols: int, rows: int) -> Tuple[int, int, int]:
        """Calculate the ideal cell size and margins to center the map."""
        tile_size = min(self.width // cols, (self.height - 40) // rows)
        off_x = (self.width - (cols * tile_size)) // 2
        off_y = ((self.height - 40 - (rows * tile_size)) // 2) + 40
        return tile_size, off_x, off_y

    def draw_maze(
        self,
        surface: pygame.Surface,
        grid: List[List[int]],
        tile_size: int,
        off_x: int,
        off_y: int
    ) -> None:
        """Draw the walls of the maze while preserving the
        individual bits of each cell."""
        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 1

        for r in range(rows):
            for c in range(cols):
                val = grid[r][c]
                x = off_x + (c * tile_size)
                y = off_y + (r * tile_size)

                if val == 15:
                    rect = pygame.Rect(x, y, tile_size, tile_size)
                    pygame.draw.rect(surface, self.COLOR_WALL,
                                     rect, width=2, border_radius=3)

                elif val > 0:
                    if val & 1:
                        pygame.draw.line(surface, self.COLOR_WALL,
                                         (x, y), (x + tile_size, y), 2)

                    if val & 2:
                        pygame.draw.line(surface, self.COLOR_WALL,
                                         (x + tile_size, y),
                                         (x + tile_size, y + tile_size), 2)

                    if val & 4:
                        pygame.draw.line(surface, self.COLOR_WALL,
                                         (x, y + tile_size),
                                         (x + tile_size, y + tile_size), 2)

                    if val & 8:
                        pygame.draw.line(surface, self.COLOR_WALL,
                                         (x, y), (x, y + tile_size), 2)

    def draw_collectibles(
            self, surface: pygame.Surface, collectibles: List[Collectible],
            tile_size: int, off_x: int, off_y: int) -> None:
        """Draw the Pacgums and Superpacgums."""
        for item in collectibles:
            cx, cy = item.cell
            center_x = off_x + (cx * tile_size) + (tile_size // 2)
            center_y = off_y + (cy * tile_size) + (tile_size // 2)

            if item.sprite_id == "superpacgum":
                pygame.draw.circle(
                    surface, self.COLOR_SUPER_PACGUM,
                    (center_x, center_y), max(4, tile_size // 4))
            else:
                pygame.draw.circle(
                    surface, self.COLOR_PACGUM,
                    (center_x, center_y), max(2, tile_size // 8))

    def draw_player(self, surface: pygame.Surface, player: Player,
                    tile_size: int, off_x: int, off_y: int) -> None:
        """Draw Pac-Man by smoothly interpolating his position
        using the `progress` function."""
        px, py = float(player.cell[0]), float(player.cell[1])
        if player.direction is not None:
            px += player.direction.dx * player.progress
            py += player.direction.dy * player.progress

        screen_x = int(off_x + (px * tile_size))
        screen_y = int(off_y + (py * tile_size))

        if "player" in self.sprites:
            angle = self.ROTATIONS.get(player.direction or
                                       player.facing_direction, 0)
            rotated = pygame.transform.rotate(self.sprites["player"], angle)
            surface.blit(rotated, (screen_x, screen_y))
        else:
            center = (screen_x + tile_size // 2, screen_y + tile_size // 2)
            pygame.draw.circle(
                surface, self.COLOR_PACMAN,
                center, max(4, tile_size // 2 - 2))

    def draw_ghosts(self, surface: pygame.Surface, ghosts: List[Ghost],
                    tile_size: int, off_x: int, off_y: int) -> None:
        """Draw the ghosts with smooth animation between frames."""
        for ghost in ghosts:
            gx, gy = float(ghost.cell[0]), float(ghost.cell[1])
            if ghost.direction is not None:
                gx += ghost.direction.dx * ghost.progress
                gy += ghost.direction.dy * ghost.progress

            screen_x = int(off_x + (gx * tile_size))
            screen_y = int(off_y + (gy * tile_size))

            if ghost.state == GhostState.EATEN:
                sprite_key = "eaten"
            elif ghost.state == GhostState.FRIGHTENED:
                sprite_key = "frightened"
            else:
                sprite_key = ghost.ghost_type.lower()

            if sprite_key in self.sprites:
                surface.blit(self.sprites[sprite_key], (screen_x, screen_y))
            else:

                if ghost.state == GhostState.EATEN:
                    eye_y = screen_y + tile_size // 2
                    eye_r = max(2, tile_size // 6)
                    
                    pygame.draw.circle(surface, (255, 255, 255), (screen_x + tile_size // 3, eye_y), eye_r)
                    pygame.draw.circle(surface, (255, 255, 255), (screen_x + 2 * tile_size // 3, eye_y), eye_r)
                    
                    pupil_r = max(1, eye_r // 2)
                    pygame.draw.circle(surface, (0, 0, 255), (screen_x + tile_size // 3, eye_y), pupil_r)
                    pygame.draw.circle(surface, (0, 0, 255), (screen_x + 2 * tile_size // 3, eye_y), pupil_r)

                else:
                    color = (
                        self.GHOST_COLORS["frightened"]
                        if ghost.state == GhostState.FRIGHTENED
                        else self.GHOST_COLORS.get(ghost.ghost_type, (255, 0, 0))
                    )
                    head_center = (screen_x + tile_size // 2, screen_y + tile_size // 3)
                    pygame.draw.circle(surface, color, head_center, tile_size // 3)
                    pygame.draw.rect(
                        surface, color, 
                        (screen_x + 2, screen_y + tile_size // 3, tile_size - 4, tile_size // 2)
                    )

                    eye_y = screen_y + tile_size // 3
                    eye_r = max(1, tile_size // 8)
                    pygame.draw.circle(surface, (255, 255, 255), (screen_x + tile_size // 3, eye_y), eye_r)
                    pygame.draw.circle(surface, (255, 255, 255), (screen_x + 2 * tile_size // 3, eye_y), eye_r)


''''

                color = (
                    self.GHOST_COLORS["frightened"]
                    if ghost.state == GhostState.FRIGHTENED
                    else self.GHOST_COLORS.get(ghost.ghost_type, (255, 0, 0))
                )
                head_center = (screen_x + tile_size // 2,
                               screen_y + tile_size // 3)
                pygame.draw.circle(surface, color, head_center, tile_size // 3)
                pygame.draw.rect(
                    surface, color, (screen_x + 2, screen_y + tile_size
                                     // 3, tile_size - 4, tile_size // 2))

                eye_y = screen_y + tile_size // 3
                eye_r = max(1, tile_size // 8)
                pygame.draw.circle(
                    surface, (255, 255, 255),
                    (screen_x + tile_size // 3, eye_y), eye_r)
                pygame.draw.circle(
                    surface, (255, 255, 255),
                    (screen_x + 2 * tile_size // 3, eye_y), eye_r)
'''