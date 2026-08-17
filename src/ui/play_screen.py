from typing import Any, Optional
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
    """Manages the main active gameplay state, level lifecycle,
    and game loop integration.

    Acts as the primary coordinator for `GameState.PLAYING`.
    It handles user input processing, game physics updates,
    maze generation, level transitions, and delegate rendering
    for entities (player, ghosts, collectibles) alongside the HUD.
    """

    def __init__(self, screen_width: int, screen_height: int,
                 config_or_data: Any = None) -> None:

        """Initializes the playing screen, visual rendering engine,
        and core game components.

        Args:
            screen_width: The display width in pixels.
            screen_height: The display height in pixels.
            config_or_data: Dictionary containing game
                            configuration parameters parsed from JSON.
        """
        super().__init__(screen_width, screen_height)

        self.config = (
            config_or_data if isinstance(config_or_data, dict) else {}
        )
        self.clock = pygame.time.Clock()
        self.input_handler = InputHandler()
        self.hud = HUD(screen_width, screen_height)
        self.renderer = Renderer(screen_width, screen_height)

        self.current_level_index: int = 0
        self.game_progression: Optional[GameProgression] = None
        self.game: Optional[Game] = None

        self._parse_global_config()
        self.reset()

    def _parse_global_config(self) -> None:
        """Extracts global gameplay parameters from the
        configuration dictionary.

        Populates instance attributes with fallback values
        for player lives, pacgum counts,
        scoring rules, time limits, generation seeds,
        and stage dimensions.
        """

        cfg = self.config
        self.default_lives = cfg.get("lives", 3)
        self.pacgum_quantity = cfg.get("pacgum", 42)
        self.pacgum_pts = cfg.get("points_per_pacgum", 10)
        self.superpacgum_pts = cfg.get("points_per_super_pacgum", 50)
        self.ghost_pts = cfg.get("points_per_ghost", 200)
        self.time_limit = float(cfg.get("level_max_time", 90))
        self.seed = cfg.get("seed", 42)
        self.level_configs = cfg.get("level", [])

    def _load_level(self,
                    score: int = 0,
                    lives: Optional[int] = None) -> None:
        """Generates the maze layout and instantiates the active
        Level and Game objects. Determines grid dimensions and seeds
        based on the level index, calls the maze loader, instantiates
        `Level` and `Game`, and reconfigures the tile renderer scaling.

        Args:
            score: The player's accumulated score carried over to this level.
            Defaults to 0.
            lives: Remaining player lives carried over. Defaults to
            `self.default_lives` if None.
        """

        if self.level_configs:
            idx = min(self.current_level_index, len(self.level_configs) - 1)
            lvl_cfg = self.level_configs[idx]
            width, height = lvl_cfg["width"], lvl_cfg["height"]
        else:
            width, height = 21, 21

        current_seed = (
            self.seed
            if self.current_level_index == 0
            else random.randint(1, 1000000)
        )

        try:
            maze_data = load_maze(width=width,
                                  height=height,
                                  seed=current_seed)
        except Exception as err:
            raise ValueError(
                f"[Warning] No se pudo generar el laberinto: {err}"
            ) from err

        level = Level(
            grid=maze_data.grid,
            pacgum_quantity=self.pacgum_quantity,
            pacgum_points=self.pacgum_pts,
            superpacgum_points=self.superpacgum_pts,
            ghost_points=self.ghost_pts,
            time_left=self.time_limit
        )

        current_lives = lives if lives is not None else self.default_lives
        self.game = Game(level=level, lives=current_lives, score=score)

        self._update_renderer_layout()

    def _update_renderer_layout(self) -> None:
        """Recalculates tile dimensions and updates sprite assets
        to fit the active grid layout."""
        grid = self.game.level.grid if self.game else []
        cols = len(grid[0]) if grid else 1
        rows = len(grid) if grid else 1
        tile_size, _, _ = self.renderer.get_layout(cols, rows)
        self.renderer.load_sprites_for_tile_size(tile_size)

    def handle_event(self, event: pygame.event.Event) -> Optional[GameState]:
        """Processes key presses, developer shortcuts,
        and player direction inputs.

        Args:
            event: The Pygame event to evaluate.
        Returns:
            Optional[GameState]: `GameState.PAUSED` if pause requested,
            otherwise `GameState.PLAYING`.
        """
        if event.type == pygame.KEYDOWN and event.key in (
            pygame.K_p, pygame.K_ESCAPE
        ):
            return GameState.PAUSED

        if self.game is None:
            return GameState.PLAYING

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:
                self.game.player.invincible_switch()
            if event.key == pygame.K_n:
                self.game.level.force_complete()

        requested_dir = self.input_handler.process_event(event)
        if requested_dir is not None:
            self.game.player.set_desired_direction(requested_dir)

        return GameState.PLAYING

    def update(self) -> GameState:
        """Advances the game physics simulation and evaluates level
        completion or game over states. Calculates frame delta time,
        updates internal game logic, and checks win/loss conditions.

        Returns:
            GameState: The active state (`PLAYING`, `GAME_OVER`, or `WIN`).
        """
        if self.game is None:
            return GameState.PLAYING

        dt = min(self.clock.tick(60) / 1000.0, 0.1)
        self.game._update(dt)

        if self.game.is_running:
            return GameState.PLAYING

        if self.game.lives <= 0 or self.game.level.time_left <= 0:
            return GameState.GAME_OVER

        if self.game.level.is_completed():
            return self._advance_to_next_level()

        return GameState.PLAYING

    def _advance_to_next_level(self) -> GameState:
        """Progresses the session to the next level while preserving
        score and remaining lives.
        Returns:
            GameState: `GameState.PLAYING` if a new level is loaded,
            or `GameState.WIN` if all levels in the progression
            have been completed.
        """
        if self.game_progression is None or self.game is None:
            return GameState.WIN

        if not self.game_progression.next_level():
            return GameState.WIN

        saved_score = self.game.score
        saved_lives = self.game.lives
        self.current_level_index += 1

        self._load_level(score=saved_score, lives=saved_lives)
        return GameState.PLAYING

    def reset(self) -> None:
        """Restores the screen state to Level 1 with a new progression
        instance, score, and lives."""
        self.current_level_index = 0
        self.game_progression = GameProgression()
        self._load_level()

    def on_enter(self, previous_state: GameState) -> None:
        """Lifecycle hook triggered when transitioning into this screen.

        Resumes the frame clock if returning from pause,
        or triggers a full reset if coming from menus or end-game screens.

        Args:
            previous_state: The application state prior to entering
            `GameState.PLAYING`.
        """
        if previous_state == GameState.PAUSED:
            self.clock.tick()
        else:
            self.reset()

    def draw(self, surface: pygame.Surface) -> None:
        """Renders all game elements, entities, background,
        and HUD onto the target surface.
        Args:
            surface: The main Pygame display surface to draw on.
        """
        surface.fill((0, 0, 0))

        if self.game is None:
            return

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
