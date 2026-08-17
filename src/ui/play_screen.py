from typing import Any, List, Optional, Tuple
import pygame
import random

from src.core.game import Game
from src.core.level import Level
from src.core.progression import GameProgression
from src.level_manager.maze_loader import load_maze
from src.states import GameState
from src.ui.hud import HUD
from src.ui.input_handler import InputHandler
from src.ui.menus.base_screen import BaseScreen
from src.ui.renderer import Renderer


class PlayScreen(BaseScreen):
    """Controls the game's visual flow by reading
    the dynamic JSON configuration"""

    def __init__(self, screen_width: int, screen_height: int,
                 config_or_data: Any = None) -> None:
        super().__init__(screen_width, screen_height)

        self.config = config_or_data
        self.clock = pygame.time.Clock()
        self.current_level_index: int = 0

        self.input_handler = InputHandler()
        self.hud = HUD(screen_width, screen_height)
        self.renderer = Renderer(screen_width, screen_height)
        self.w, self.h = 0, 0

        (self.grid, self.lives, self.pacgum_quantity, self.pacgum_pts,
         self.superpacgum_pts, self.ghost_pts, self.time_limit) = (
            self._parse_config(config_or_data))

        self.level = Level(
            grid=self.grid,
            pacgum_quantity=self.pacgum_quantity,
            pacgum_points=self.pacgum_pts,
            superpacgum_points=self.superpacgum_pts,
            ghost_points=self.ghost_pts,
            time_left=self.time_limit
        )
        self.game = Game(level=self.level, lives=self.lives)
        self.game_progression = GameProgression()

        cols = len(self.grid[0]) if self.grid else 1
        rows = len(self.grid) if self.grid else 1
        tile_size, _, _ = self.renderer.get_layout(cols, rows)
        self.renderer.load_sprites_for_tile_size(tile_size)

    def _parse_config(self, config_or_data: Any) -> Tuple[
         List[List[int]], int, int, int, int, int, float]:
        """Retrieve the array and parameters, assuming that
        config_parser has already parsed the JSON."""
        if isinstance(config_or_data, dict):
            lives = config_or_data.get("lives", 3)
            pacgum_quantity = self.config.get("pacgum", 42)
            pacgum_pts = config_or_data.get("points_per_pacgum", 10)
            superpacgum_pts = config_or_data.get("points_per_super_pacgum", 50)
            time_limit = float(config_or_data.get("level_max_time", 90))
            seed = config_or_data.get("seed", 42)
            ghost_points = config_or_data.get("points_per_ghost", 200)
            levels = config_or_data.get("level", [])
            if levels and self.current_level_index < len(levels):
                lvl_cfg = levels[self.current_level_index]
                self.w, self.h = lvl_cfg["width"], lvl_cfg["height"]
            else:
                self.w, self.h = 21, 21
            try:
                maze_data = load_maze(width=self.w, height=self.h, seed=seed)
                self.grid = maze_data.grid
            except Exception as err:
                print(f"[Warning] No se pudo generar el laberinto: {err}")
                self.grid = self._get_default_grid()
            return (self.grid, lives, pacgum_quantity, pacgum_pts,
                    superpacgum_pts, ghost_points, time_limit)
        return self._get_default_grid(), 3, 42, 10, 50, 200, 90.0

    def handle_event(self, event: pygame.event.Event) -> Optional[GameState]:
        """Manages the player's pause and controls."""
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_p,
                                                          pygame.K_ESCAPE):
            return GameState.PAUSED

        if event.type == pygame.KEYDOWN and event.key == pygame.K_i:
            self.game.player.invincible_switch()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_n:
            self.game.level.force_complete()

        requested_dir = self.input_handler.process_event(event)
        if requested_dir is not None:
            self.game.player.set_desired_direction(requested_dir)

        return GameState.PLAYING

    def update(self) -> Any:
        """Update the physics and check the end of the game.
        Return GameState or None to comply with BaseScreen."""
        raw_dt = self.clock.tick(60) / 1000.0
        dt = min(raw_dt, 0.1)

        self.game._update(dt)

        if not self.game.is_running:
            if self.game.lives <= 0 or self.game.level.time_left <= 0:
                state: GameState = GameState.GAME_OVER
                return state
            elif self.game.level.is_completed():
                if self.game_progression.next_level():
                    saved_score = self.game.score
                    saved_lives = self.game.lives
                    try:
                        maze_data = load_maze(width=self.w,
                                              height=self.h,
                                              seed=random.randint(1, 1000000))
                        self.grid = maze_data.grid
                        self.level = Level(
                            grid=self.grid,
                            pacgum_quantity=self.pacgum_quantity,
                            pacgum_points=self.pacgum_pts,
                            superpacgum_points=self.superpacgum_pts,
                            ghost_points=self.ghost_pts,
                            time_left=self.time_limit
                        )
                        self.game = Game(level=self.level, lives=saved_lives,
                                         score=saved_score)
                        self.current_level_index += 1
                    except Exception as err:
                        print("[Warning] No se pudo generar "
                              f"el laberinto: {err}")
                        self.grid = self._get_default_grid()
                else:
                    state = GameState.WIN
                    return state
        state_playing: GameState = GameState.PLAYING
        return state_playing

    def reset(self) -> None:
        """Reset the level, score, and lives."""
        (self.grid, self.lives, self.pacgum_quantity, self.pacgum_pts,
         self.superpacgum_pts, self.ghost_pts,
         self.time_limit) = self._parse_config(self.config)

        self.level = Level(
            grid=self.grid,
            pacgum_quantity=self.pacgum_quantity,
            pacgum_points=self.pacgum_pts,
            superpacgum_points=self.superpacgum_pts,
            ghost_points=self.ghost_pts,
            time_left=self.time_limit
        )
        self.game = Game(level=self.level, lives=self.lives)
        self.current_level_index = 0

    def on_enter(self, previous_state: GameState) -> None:
        """Restart the game if we haven't just paused it."""
        if previous_state == GameState.PAUSED:
            self.clock.tick()
        else:
            self.reset()

    def draw(self, surface: pygame.Surface) -> None:
        """Full delegation of painting to the Renderer and HUD."""
        surface.fill((0, 0, 0))

        grid = self.game.level.grid
        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 1

        tile_size, off_x, off_y = self.renderer.get_layout(cols, rows)

        self.renderer.draw_maze(surface, grid, tile_size, off_x, off_y)
        self.renderer.draw_collectibles(surface, self.game.level.collectibles,
                                        tile_size, off_x, off_y)
        self.renderer.draw_player(surface, self.game.player, tile_size,
                                  off_x, off_y)
        self.renderer.draw_ghosts(surface, self.game.ghosts, tile_size,
                                  off_x, off_y)

        self.hud.draw(
            surface=surface,
            score=self.game.score,
            lives=self.game.lives,
            level=self.current_level_index + 1,
            time_remaining=int(self.game.level.time_left),
            invincible=self.game.player.is_invincible
        )

    def _get_default_grid(self) -> List[List[int]]:
        """Fail-safe grid."""
        return [
            [15] * 19,
            [15] + [0] * 17 + [15],
            [15, 0, 15, 15, 0, 15, 15, 15, 0, 15, 0, 15, 15, 15,
             0, 15, 15, 0, 15],
            [15, 0, 15, 15, 0, 15, 15, 15, 0, 15, 0, 15, 15, 15,
             0, 15, 15, 0, 15],
            [15] + [0] * 17 + [15],
            [15] * 19,
        ]
