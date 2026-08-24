import math
import pygame
from typing import Any, Optional
from src.states import GameState
from src.ui.menus import (
    MainMenu,
    HighscoresMenu,
    InstructionsMenu,
    BaseScreen,
    PauseMenu,
    GameOverScreen,
    WinScreen
)
from src.ui.play_screen import PlayScreen


class App:
    """Main application: window, screen registry, and app state machine."""

    def __init__(self, config: dict[str, Any]):
        pygame.init()
        pygame.font.init()
        self.config = config

        self.VIRTUAL_WIDTH = 800
        self.VIRTUAL_HEIGHT = 600
        self.virtual_screen = pygame.Surface(
            (self.VIRTUAL_WIDTH,
             self.VIRTUAL_HEIGHT)
            )

        window_cfg = config.get("window") or {}
        self.real_width, self.real_height = self._resolve_window_size(
            window_cfg.get("width"), window_cfg.get("height"))
        self.fps = window_cfg.get("fps") or 60

        self.screen = pygame.display.set_mode(
            (self.real_width, self.real_height), pygame.RESIZABLE
        )
        pygame.display.set_caption("Pac-Man 42")
        self.clock = pygame.time.Clock()

        self.state = GameState.MENU
        self.is_running = True
        self.highscore_file: str = self.config.get(
            "highscore_filename", "highscores.json"
        )
        self.crt_overlay = self._build_crt_overlay(
            self.VIRTUAL_WIDTH, self.VIRTUAL_HEIGHT)
        self.screens = self._build_screens()

    @staticmethod
    def _resolve_window_size(width: Optional[int],
                             height: Optional[int]) -> tuple[int, int]:
        """Return the configured window size, or a 4:3 size that fits
        80% of the desktop."""
        desktop_w, desktop_h = 1920, 1080
        try:
            sizes = pygame.display.get_desktop_sizes()
            if sizes:
                desktop_w, desktop_h = sizes[0]
        except pygame.error:
            pass

        if isinstance(width, int) and isinstance(height, int):
            return (min(max(width, 400), desktop_w),
                    min(max(height, 300), desktop_h))

        win_h = int(desktop_h * 0.8)
        win_w = int(win_h * 4 / 3)
        if win_w > desktop_w:
            win_w = desktop_w
            win_h = int(win_w * 3 / 4)
        return win_w, win_h

    def _build_screens(self) -> dict[GameState, BaseScreen]:
        """Instantiate every screen once, keyed by application state."""
        return {
            GameState.MENU: MainMenu(self.VIRTUAL_WIDTH, self.VIRTUAL_HEIGHT,
                                     self.highscore_file),
            GameState.INSTRUCTIONS: InstructionsMenu(self.VIRTUAL_WIDTH,
                                                     self.VIRTUAL_HEIGHT),
            GameState.HIGHSCORES: HighscoresMenu(self.VIRTUAL_WIDTH,
                                                 self.VIRTUAL_HEIGHT,
                                                 self.highscore_file),
            GameState.PLAYING: PlayScreen(self.VIRTUAL_WIDTH,
                                          self.VIRTUAL_HEIGHT,
                                          self.config),
            GameState.PAUSED: PauseMenu(self.VIRTUAL_WIDTH,
                                        self.VIRTUAL_HEIGHT),
            GameState.GAME_OVER: GameOverScreen(self.VIRTUAL_WIDTH,
                                                self.VIRTUAL_HEIGHT,
                                                self.highscore_file),
            GameState.WIN: WinScreen(self.VIRTUAL_WIDTH,
                                     self.VIRTUAL_HEIGHT,
                                     self.highscore_file),
        }

    def run(self) -> None:
        """Run the core application loop until quit, then shut down Pygame."""
        while self.is_running:
            self._handle_events()
            self._update()
            self._render()
            self.clock.tick(self.fps)
        pygame.quit()

    def _change_state(self, new_state: GameState) -> None:
        """Apply a state transition and fire the screen's on_enter hook."""

        if new_state == GameState.QUIT:
            self.is_running = False
            return

        previous_state = self.state
        self.state = new_state

        target_screen = self.screens.get(new_state)

        if target_screen and new_state in (GameState.GAME_OVER, GameState.WIN):
            play_screen = self.screens.get(GameState.PLAYING)
            if play_screen and hasattr(target_screen, "set_final_score"):
                final_score = getattr(play_screen, "game", None)
                score_val = final_score.score if final_score else 0
                target_screen.set_final_score(score_val)

        if target_screen:
            target_screen.on_enter(previous_state)

    def _handle_events(self) -> None:
        """Process system events and delegate the rest to the active screen."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

            elif event.type == pygame.VIDEORESIZE:
                # SDL2 resizes the display surface on its own; calling
                # set_mode here recreates the window and loops forever
                # on tiling WMs (Hyprland/i3/sway).
                if event.w > 0 and event.h > 0:
                    self.real_width, self.real_height = event.w, event.h

            else:
                current_screen = self.screens.get(self.state)
                if current_screen:
                    new_state = current_screen.handle_event(event)
                    if (new_state is None and event.type == pygame.KEYDOWN
                            and event.key == pygame.K_ESCAPE):
                        self.is_running = False
                    elif new_state is not None and new_state != self.state:
                        self._change_state(new_state)

    def _update(self) -> None:
        """Update the active screen and apply any requested transition."""
        current_screen = self.screens.get(self.state)
        if current_screen:
            new_state = current_screen.update()
            if new_state and new_state != self.state:
                self._change_state(new_state)

    @staticmethod
    def _build_crt_overlay(width: int, height: int) -> pygame.Surface:
        """Pre-build the CRT effect: scanlines plus an edge vignette."""
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)

        for y in range(0, height, 3):
            pygame.draw.line(overlay, (5, 2, 12, 26), (0, y), (width, y))

        small_w, small_h = max(1, width // 8), max(1, height // 8)
        vignette = pygame.Surface((small_w, small_h), pygame.SRCALPHA)
        cx, cy = small_w / 2, small_h / 2
        max_dist = math.hypot(cx, cy)
        for y in range(small_h):
            for x in range(small_w):
                dist = math.hypot(x - cx, y - cy) / max_dist
                alpha = int(max(0.0, (dist - 0.55) / 0.45) ** 2.2 * 240)
                vignette.set_at((x, y), (5, 2, 12, alpha))
        overlay.blit(pygame.transform.smoothscale(
            vignette, (width, height)), (0, 0))

        return overlay

    def _render(self) -> None:
        """Render the active screen and letterbox it into the window."""
        if self.real_width <= 0 or self.real_height <= 0:
            return

        self.virtual_screen.fill((0, 0, 0))

        current_screen = self.screens.get(self.state)
        if current_screen:
            current_screen.draw(self.virtual_screen)

        self.virtual_screen.blit(self.crt_overlay, (0, 0))

        self.screen.fill((0, 0, 0))
        scale = min(self.real_width / self.VIRTUAL_WIDTH,
                    self.real_height / self.VIRTUAL_HEIGHT)
        scaled_size = (int(self.VIRTUAL_WIDTH * scale),
                       int(self.VIRTUAL_HEIGHT * scale))
        scaled_surface = pygame.transform.scale(self.virtual_screen,
                                                scaled_size)

        pos_x = (self.real_width - scaled_size[0]) // 2
        pos_y = (self.real_height - scaled_size[1]) // 2

        self.screen.blit(scaled_surface, (pos_x, pos_y))
        pygame.display.flip()
