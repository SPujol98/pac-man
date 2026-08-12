from typing import Optional, List
import pygame
from src.states import GameState, Direction
from src.ui.menus.base_screen import BaseScreen
from src.ui.renderer import Renderer
from src.ui.hud import HUD
from src.ui.input_handler import InputHandler
from src.entities.player import Player
from src.entities.ghost import Ghost


class PlayScreen(BaseScreen):
    """Gestiona el ciclo de vida del juego cuando el estado es GameState.PLAYING."""

    def __init__(self, screen_width: int, screen_height: int, maze_data: dict):
        super().__init__(screen_width, screen_height)

        self.maze_data = maze_data

        self.input_handler = InputHandler()
        self.renderer = Renderer(screen_width, screen_height)
        self.hud = HUD(screen_width, screen_height)

        self.clock = pygame.time.Clock()

        # Variables globales de la partida
        self.score: int = 0
        self.lives: int = 3
        self.level_num: int = 1
        self.time_remaining: float = 90.0

        self.player = Player(cell=(1, 1), speed=5.0, lives=self.lives)


        self.ghosts: List[Ghost] = [
            Ghost(
                cell=(9, 9),
                ghost_type="blinky",
                speed=4.5,
                scatter_corner=(18, 0),
                house_entrance=(9, 8)
            ),
            Ghost(
                cell=(10, 9),
                ghost_type="pinky",
                speed=4.5,
                scatter_corner=(0, 0),
                house_entrance=(9, 8)
            ),
            Ghost(
                cell=(9, 10),
                ghost_type="inky",
                speed=4.5,
                scatter_corner=(18, 18),
                house_entrance=(9, 8)
            ),
            Ghost(
                cell=(10, 10),
                ghost_type="clyde",
                speed=4.5,
                scatter_corner=(0, 18),
                house_entrance=(9, 8)
            )
        ]

    def handle_event(self, event: pygame.event.Event) -> Optional[GameState]:
        """Procesa las entradas durante la partida."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                return GameState.PAUSED

            requested_dir = self.input_handler.process_event(event)
            if requested_dir is not None:
                self.player.set_desired_direction(requested_dir)

        return GameState.PLAYING

    def update(self) -> None:
        """Actualiza el movimiento y estado de todas las entidades."""

        dt = self.clock.tick(60) / 1000.0

        self.time_remaining = max(0.0, self.time_remaining - dt)

        self.player.update(dt=dt, level=self.maze_data)

        for ghost in self.ghosts:
            ghost.update(dt=dt, level=self.maze_data, player=self.player)

    def draw(self, surface: pygame.Surface) -> None:
        """Renderiza el mapa, entidades y HUD."""
        surface.fill((0, 0, 0))

        grid = self.maze_data.grid
        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 1

        self.renderer.draw_maze(surface, grid)

        player_dir = self.player.direction or Direction.RIGHT
        self.renderer.draw_pacman(
            surface=surface,
            grid_pos=self.player.cell,
            direction=player_dir,
            cols=cols,
            rows=rows
        )

        for ghost in self.ghosts:
            self.renderer.draw_ghost(
                surface=surface,
                ghost_name=ghost.ghost_type,
                grid_pos=ghost.cell,
                state=ghost.state,
                cols=cols,
                rows=rows
            )

        self.hud.draw(
            surface=surface,
            score=self.score,
            lives=self.player.lives,
            level=self.level_num,
            time_remaining=int(self.time_remaining)
        )

"""Pantalla de juego activo (PLAYING) adaptada a la configuración dinámica."""
'''
from typing import Optional, List, Any
import pygame
from src.states import GameState, Direction
from src.ui.menus.base_screen import BaseScreen
from src.ui.renderer import Renderer
from src.ui.hud import HUD
from src.ui.input_handler import InputHandler
from src.entities.player import Player
from src.entities.ghost import Ghost
from src.level_manager.maze_loader import load_maze


class PlayScreen(BaseScreen):
    """Gestiona el ciclo de vida del juego utilizando la configuración de config.json."""

    def __init__(self, screen_width: int, screen_height: int, config: dict):
        super().__init__(screen_width, screen_height)

        self.config = config

        self.input_handler = InputHandler()
        self.renderer = Renderer(screen_width, screen_height)
        self.hud = HUD(screen_width, screen_height)
        self.clock = pygame.time.Clock()

        self.score: int = 0
        self.lives: int = config.get("lives", 3)
        self.level_index: int = 0

        self.max_time: float = float(config.get("level_max_time", 90))
        self.time_remaining: float = self.max_time

        self.maze_data = self._load_current_level_maze()

        self.player = Player(cell=(1, 1), speed=5.0, lives=self.lives)

        self.ghosts: List[Ghost] = [
            Ghost(cell=(9, 9), ghost_type="blinky", speed=4.5, scatter_corner=(18, 0), house_entrance=(9, 8)),
            Ghost(cell=(10, 9), ghost_type="pinky", speed=4.5, scatter_corner=(0, 0), house_entrance=(9, 8)),
            Ghost(cell=(9, 10), ghost_type="inky", speed=4.5, scatter_corner=(18, 18), house_entrance=(9, 8)),
            Ghost(cell=(10, 10), ghost_type="clyde", speed=4.5, scatter_corner=(0, 18), house_entrance=(9, 8))
        ]

    def _load_current_level_maze(self) -> Any:
        """Carga el laberinto tomando el ancho y alto correspondientes al nivel actual."""
        levels_list = self.config.get("level", [{"width": 21, "height": 21}])

        if self.level_index >= len(levels_list):
            self.level_index = len(levels_list) - 1

        current_level_cfg = levels_list[self.level_index]

        width = int(current_level_cfg.get("width", 21))
        height = int(current_level_cfg.get("height", 21))
        seed = int(self.config.get("seed", 42))

        return load_maze(width=width, height=height, seed=seed)

    def handle_event(self, event: pygame.event.Event) -> Optional[GameState]:
        """Procesa entradas durante la partida."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                return GameState.PAUSED

            requested_dir = self.input_handler.process_event(event)
            if requested_dir is not None:
                self.player.set_desired_direction(requested_dir)

        return GameState.PLAYING

    def update(self) -> None:
        """Actualiza la lógica y el temporizador basado en config."""
        dt = self.clock.tick(60) / 1000.0

        self.time_remaining = max(0.0, self.time_remaining - dt)

        self.player.update(dt=dt, level=self.maze_data)
        for ghost in self.ghosts:
            ghost.update(dt=dt, level=self.maze_data, player=self.player)

    def draw(self, surface: pygame.Surface) -> None:
        """Renderiza elementos y pasa los valores dinámicos al HUD."""
        surface.fill((0, 0, 0))

        grid = self.maze_data.grid
        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 1

        self.renderer.draw_maze(surface, grid)

        player_dir = self.player.direction or Direction.RIGHT
        self.renderer.draw_pacman(surface, self.player.cell, player_dir, cols, rows)

        for ghost in self.ghosts:
            self.renderer.draw_ghost(surface, ghost.ghost_type, ghost.cell, ghost.state, cols, rows)

        self.hud.draw(
            surface=surface,
            score=self.score,
            lives=self.player.lives,
            level=self.level_index + 1,
            time_remaining=int(self.time_remaining)
        )'''