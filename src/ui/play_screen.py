from typing import Optional, Any, List, Tuple
import pygame

from src.states import GameState
from src.ui.menus.base_screen import BaseScreen
from src.ui.input_handler import InputHandler
from src.ui.hud import HUD
from src.ui.renderer import Renderer

from src.core.game import Game
from src.core.level import Level
from src.level_manager.maze_loader import load_maze


class PlayScreen(BaseScreen):
    """Controla el flujo visual de la partida leyendo la configuración dinámica del JSON."""

    def __init__(self, screen_width: int, screen_height: int, config_or_data: Any = None) -> None:
        super().__init__(screen_width, screen_height)

        self.clock = pygame.time.Clock()
        self.current_level_index: int = 0

        self.input_handler = InputHandler()
        self.hud = HUD(screen_width, screen_height)
        self.renderer = Renderer(screen_width, screen_height)

        grid, lives, pacgum_pts, superpacgum_pts, time_limit = self._parse_config(config_or_data)

        self.level = Level(
            grid=grid,
            pacgum_points=pacgum_pts,
            superpacgum_points=superpacgum_pts,
            time_left=time_limit
        )
        self.game = Game(level=self.level, lives=lives)

        cols = len(grid[0]) if grid else 1
        rows = len(grid) if grid else 1
        tile_size, _, _ = self.renderer.get_layout(cols, rows)
        self.renderer.load_sprites_for_tile_size(tile_size)

    def _parse_config(self, config_or_data: Any) -> Tuple[List[List[int]], int, int, int, float]:
        """Extrae vidas, tiempos, puntos y genera el laberinto según la configuración cargada."""
        lives = 3
        pacgum_pts = 10
        superpacgum_pts = 50
        time_limit = 90.0
        grid = None

        if isinstance(config_or_data, dict):

            lives = config_or_data.get("lives", lives)
            pacgum_pts = config_or_data.get("points_per_pacgum", pacgum_pts)
            superpacgum_pts = config_or_data.get("points_per_super_pacgum", superpacgum_pts)
            time_limit = float(config_or_data.get("level_max_time", time_limit))
            seed = config_or_data.get("seed", 42)

            if "grid" in config_or_data:
                grid = config_or_data["grid"]
            elif "maze_grid" in config_or_data:
                grid = config_or_data["maze_grid"]
            else:
                levels = config_or_data.get("level", [])
                if levels and self.current_level_index < len(levels):
                    lvl_cfg = levels[self.current_level_index]
                    w = int(lvl_cfg.get("width", 21))
                    h = int(lvl_cfg.get("height", 21))
                else:
                    maze_cfg = config_or_data.get("maze", {})
                    w = int(maze_cfg.get("width", 21))
                    h = int(maze_cfg.get("height", 21))

                try:
                    maze_data = load_maze(width=w, height=h, seed=seed)
                    grid = maze_data.grid
                except Exception as err:
                    print(f"[Warning] No se pudo generar el laberinto con load_maze: {err}")
                    grid = None

        elif hasattr(config_or_data, "grid"):
            grid = config_or_data.grid
            if hasattr(config_or_data, "lives"):
                lives = getattr(config_or_data, "lives")

        if grid is None:
            grid = self._get_default_grid()

        return grid, lives, pacgum_pts, superpacgum_pts, time_limit

    def handle_event(self, event: pygame.event.Event) -> Optional[GameState]:
        """Maneja pausa y controles del jugador."""
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_p, pygame.K_ESCAPE):
            return GameState.PAUSED

        requested_dir = self.input_handler.process_event(event)
        if requested_dir is not None:
            self.game.player.set_desired_direction(requested_dir)

        return GameState.PLAYING

    def update(self) -> Optional[GameState]:
        """Actualiza la física y revisa fin de juego."""
        dt = self.clock.tick(60) / 1000.0

        self.game._update(dt)

        if not self.game.is_running:
            if self.game.lives <= 0 or self.game.level.time_left <= 0:
                return GameState.GAME_OVER
            elif self.game.level.is_completed():
                return GameState.VICTORY

        return GameState.PLAYING

    def draw(self, surface: pygame.Surface) -> None:
        """Delegación completa del pintado a Renderer y HUD."""
        surface.fill((0, 0, 0))

        grid = self.game.level.grid
        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 1

        tile_size, off_x, off_y = self.renderer.get_layout(cols, rows)

        self.renderer.draw_maze(surface, grid, tile_size, off_x, off_y)
        self.renderer.draw_collectibles(surface, self.game.level.collectibles, tile_size, off_x, off_y)
        self.renderer.draw_player(surface, self.game.player, tile_size, off_x, off_y)
        self.renderer.draw_ghosts(surface, self.game.ghosts, tile_size, off_x, off_y)


        self.hud.draw(
            surface=surface,
            score=self.game.score,
            lives=self.game.lives,
            level=self.current_level_index + 1,
            time_remaining=int(self.game.level.time_left)
        )

    def _get_default_grid(self) -> List[List[int]]:
        """Cuadrícula de seguridad en caso de fallo."""
        return [
            [15] * 19,
            [15] + [0] * 17 + [15],
            [15, 0, 15, 15, 0, 15, 15, 15, 0, 15, 0, 15, 15, 15, 0, 15, 15, 0, 15],
            [15, 0, 15, 15, 0, 15, 15, 15, 0, 15, 0, 15, 15, 15, 0, 15, 15, 0, 15],
            [15] + [0] * 17 + [15],
            [15] * 19,
        ]