import pygame
from typing import List, Dict, Any
from src.states import Direction, GhostState

# OJO! AQUI SE PASARA PARA USAR IMAGENES!, FANTASMAS Y PAC MAN
class Renderer:
    """Transforma la matriz del laberinto y posiciones del juego en gráficos."""

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

    def get_offsets(self, cols: int, rows: int) -> tuple[int, int]:
        """Calcula el margen x/y para centrar el laberinto dejando espacio para el HUD."""
        maze_w = cols * self.tile_size
        maze_h = rows * self.tile_size
        offset_x = (self.width - maze_w) // 2
        offset_y = ((self.height - maze_h) // 2) + 20
        return offset_x, offset_y

    def draw_maze(self, surface: pygame.Surface, maze_grid: List[List[int]]) -> None:
        """Renderiza las paredes y los pacgums de la matriz del mapa."""
        if not maze_grid or not maze_grid[0]:
            return

        rows = len(maze_grid)
        cols = len(maze_grid[0])
        off_x, off_y = self.get_offsets(cols, rows)

        for r in range(rows):
            for c in range(cols):
                x = off_x + (c * self.tile_size)
                y = off_y + (r * self.tile_size)
                cell_value = maze_grid[r][c]

                if cell_value == 1:
                    rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
                    pygame.draw.rect(surface, self.COLOR_WALL, rect, width=2, border_radius=4)

                elif cell_value == 2:
                    center = (x + self.tile_size // 2, y + self.tile_size // 2)
                    pygame.draw.circle(surface, self.COLOR_PACGUM, center, 3)

                elif cell_value == 3:
                    center = (x + self.tile_size // 2, y + self.tile_size // 2)
                    pygame.draw.circle(surface, self.COLOR_SUPER_PACGUM, center, 7)

    def draw_pacman(
        self,
        surface: pygame.Surface,
        grid_pos: tuple[int, int],
        direction: Direction,
        cols: int,
        rows: int
    ) -> None:
        """Dibuja a Pac-Man en su posición de la cuadrícula."""
        off_x, off_y = self.get_offsets(cols, rows)
        x = off_x + (grid_pos[0] * self.tile_size) + (self.tile_size // 2)
        y = off_y + (grid_pos[1] * self.tile_size) + (self.tile_size // 2)
        radius = self.tile_size // 2 - 2

        pygame.draw.circle(surface, self.COLOR_PACMAN, (x, y), radius)

    def draw_ghost(
        self,
        surface: pygame.Surface,
        ghost_name: str,
        grid_pos: tuple[int, int],
        state: GhostState,
        cols: int,
        rows: int
    ) -> None:
        """Dibuja un fantasma con su color o estado de vulnerabilidad."""
        off_x, off_y = self.get_offsets(cols, rows)
        x = off_x + (grid_pos[0] * self.tile_size)
        y = off_y + (grid_pos[1] * self.tile_size)
        size = self.tile_size

        color = (
            self.GHOST_COLORS["frightened"]
            if state == GhostState.FRIGHTENED
            else self.GHOST_COLORS.get(ghost_name, (255, 0, 0))
        )

        pygame.draw.circle(surface, color, (x + size // 2, y + size // 3), size // 3)
        pygame.draw.rect(surface, color, (x + 2, y + size // 3, size - 4, size // 2))

        eye_y = y + size // 3
        pygame.draw.circle(surface, (255, 255, 255), (x + 7, eye_y), 3)
        pygame.draw.circle(surface, (255, 255, 255), (x + size - 7, eye_y), 3)