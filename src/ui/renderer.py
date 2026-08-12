from pathlib import Path
from typing import Dict, List, Tuple
import pygame
from src.states import Direction, GhostState


class Renderer:
    """Convert the maze matrix and positions into graphics using sprites."""

    def __init__(self, screen_width: int, screen_height: int, tile_size: int = 24):
        self.width = screen_width
        self.height = screen_height
        self.tile_size = tile_size


        self.COLOR_WALL = (33, 33, 222)
        self.COLOR_PACGUM = (255, 183, 174)
        self.COLOR_SUPER_PACGUM = (255, 255, 255)
        self.COLOR_PACMAN = (255, 255, 0)

        self.GHOST_COLORS = {
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
        self._load_sprites()

    def _load_sprites(self) -> None:
        """Load and resize the PNG files from the assets folder."""
        assets_dir = Path("assets/images")
        sprite_files = {
            "pacman": "pacman.png",
            "blinky": "blinky.png",
            "pinky": "pinky.png",
            "inky": "inky.png",
            "clyde": "clyde.png",
            "frightened": "frightened.png",
        }

        for key, filename in sprite_files.items():
            file_path = assets_dir / filename
            if file_path.is_file():
                try:
                    img = pygame.image.load(str(file_path)).convert_alpha()
                    scaled = pygame.transform.scale(img, (self.tile_size, self.tile_size))
                    self.sprites[key] = scaled
                except pygame.error as err:
                    print(f"[Warning] Unable to load {file_path}: {err}")

    def get_offsets(self, cols: int, rows: int) -> Tuple[int, int]:
        """Calculate the X/Y margin to center the maze while leaving space for the HUD."""
        maze_w = cols * self.tile_size
        maze_h = rows * self.tile_size
        offset_x = (self.width - maze_w) // 2
        offset_y = ((self.height - maze_h) // 2) + 20
        return offset_x, offset_y

    def draw_maze(self, surface: pygame.Surface, maze_grid: List[List[int]]) -> None:
        """Render the walls and collectibles in the maze."""
        if not maze_grid or not maze_grid[0]:
            return

        rows = len(maze_grid)
        cols = len(maze_grid[0])
        off_x, off_y = self.get_offsets(cols, rows)

        for r in range(rows):
            for c in range(cols):
                x = off_x + (c * self.tile_size)
                y = off_y + (r * self.tile_size)
                cell = maze_grid[r][c]

                if cell == 1:
                    rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
                    pygame.draw.rect(surface, self.COLOR_WALL, rect, width=2, border_radius=4)

                elif cell == 2:
                    center = (x + self.tile_size // 2, y + self.tile_size // 2)
                    pygame.draw.circle(surface, self.COLOR_PACGUM, center, 3)

                elif cell == 3:
                    center = (x + self.tile_size // 2, y + self.tile_size // 2)
                    pygame.draw.circle(surface, self.COLOR_SUPER_PACGUM, center, 7)

    def draw_pacman(
        self,
        surface: pygame.Surface,
        grid_pos: Tuple[int, int],
        direction: Direction,
        cols: int,
        rows: int
    ) -> None:
        """Draw Pac-Man facing the current direction."""
        off_x, off_y = self.get_offsets(cols, rows)
        x = off_x + (grid_pos[0] * self.tile_size)
        y = off_y + (grid_pos[1] * self.tile_size)

        if "pacman" in self.sprites:
            angle = self.ROTATIONS.get(direction, 0)
            rotated_sprite = pygame.transform.rotate(self.sprites["pacman"], angle)
            surface.blit(rotated_sprite, (x, y))
        else:
            center = (x + self.tile_size // 2, y + self.tile_size // 2)
            radius = self.tile_size // 2 - 2
            pygame.draw.circle(surface, self.COLOR_PACMAN, center, radius)

    def draw_ghost(
        self,
        surface: pygame.Surface,
        ghost_name: str,
        grid_pos: Tuple[int, int],
        state: GhostState,
        cols: int,
        rows: int
    ) -> None:
        """Draw the ghost using its sprite or the vulnerability sprite."""
        off_x, off_y = self.get_offsets(cols, rows)
        x = off_x + (grid_pos[0] * self.tile_size)
        y = off_y + (grid_pos[1] * self.tile_size)

        sprite_key = "frightened" if state == GhostState.FRIGHTENED else ghost_name.lower()

        if sprite_key in self.sprites:
            surface.blit(self.sprites[sprite_key], (x, y))
        else:
            color = (
                self.GHOST_COLORS["frightened"]
                if state == GhostState.FRIGHTENED
                else self.GHOST_COLORS.get(ghost_name.lower(), (255, 0, 0))
            )
            size = self.tile_size
            pygame.draw.circle(surface, color, (x + size // 2, y + size // 3), size // 3)
            pygame.draw.rect(surface, color, (x + 2, y + size // 3, size - 4, size // 2))

            eye_y = y + size // 3
            pygame.draw.circle(surface, (255, 255, 255), (x + 7, eye_y), 3)
            pygame.draw.circle(surface, (255, 255, 255), (x + size - 7, eye_y), 3)