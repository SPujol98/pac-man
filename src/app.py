import pygame
from typing import Any
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
from src.level_manager.maze_loader import load_maze


class App:
    """Main application manager and state machine coordinator.

    Handles Pygame subsystem initialization, resizable window configuration,
    virtual surface scaling, global event dispatching, and transitions
    between active game screens.
    """
    def __init__(self, config: dict[str, Any]):
        """Initializes Pygame display, window settings, virtual canvas,
        and screen registry.

        Args:
            config: Configuration dictionary containing window, maze layout,
            and gameplay settings.
        """
        pygame.init()
        pygame.font.init()
        self.config = config

        self.VIRTUAL_WIDTH = 800
        self.VIRTUAL_HEIGHT = 600
        self.virtual_screen = pygame.Surface(
            (self.VIRTUAL_WIDTH,
             self.VIRTUAL_HEIGHT)
            )

        window_cfg = config.get("window", {})
        self.real_width = window_cfg.get("width", 1600)
        self.real_height = window_cfg.get("height", 1200)
        self.fps = window_cfg.get("fps", 60)

        self.screen = pygame.display.set_mode(
            (self.real_width, self.real_height), pygame.RESIZABLE
        )
        pygame.display.set_caption("Pac-Man 42")
        self.clock = pygame.time.Clock()

        maze_cfg = config.get("maze", {})
        width = maze_cfg.get("width", 21)
        height = maze_cfg.get("height", 21)
        seed = maze_cfg.get("seed", 42)

        self.maze_data = load_maze(width=width, height=height, seed=seed)
        self.state = GameState.MENU
        self.is_running = True
        self.highscore_file: str = self.config.get(
            "highscore_filename", "highscores.json"
        )

        self.screens: dict[GameState, BaseScreen] = {
            GameState.MENU: MainMenu(self.VIRTUAL_WIDTH, self.VIRTUAL_HEIGHT),
            GameState.INSTRUCTIONS: InstructionsMenu(self.VIRTUAL_WIDTH,
                                                     self.VIRTUAL_HEIGHT),
            GameState.HIGHSCORES: HighscoresMenu(self.VIRTUAL_WIDTH,
                                                 self.VIRTUAL_HEIGHT,
                                                 self.highscore_file),
            GameState.PLAYING: PlayScreen(self.VIRTUAL_WIDTH,
                                          self.VIRTUAL_HEIGHT,
                                          self.highscore_file),
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
        """Executes the core application loop until execution is terminated.

        Continuously dispatches event handling, frame updates,
        surface rendering, and frame rate capping, followed by clean Pygame
        module shutdown upon exit.
        """
        while self.is_running:
            self._handle_events()
            self._update()
            self._render()
            self.clock.tick(self.fps)
        pygame.quit()

    def _change_state(self, new_state: GameState) -> None:
        """Centralizes state machine transitions and invokes screen
        lifecycle callbacks.

        Passes final scores to terminal game screens (GAME_OVER / WIN)
        when transitioning out of gameplay, and triggers the `on_enter`
        hook on the newly activated screen.

        Args:
            new_state: The target `GameState` to transition into.
        """

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
        """Processes global system inputs and delegates user inputs
        to the active screen.

        Handles application quit and window resizing events directly,
        while passing user control events to the active screen handler.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

            elif event.type == pygame.VIDEORESIZE:
                self.real_width, self.real_height = event.w, event.h
                self.screen = pygame.display.set_mode(
                    (self.real_width, self.real_height), pygame.RESIZABLE
                )

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
        """Updates internal logic and state mechanics for the active screen.

        Triggers state transitions if requested by the active screen
        during its update cycle.
        """
        current_screen = self.screens.get(self.state)
        if current_screen:
            new_state = current_screen.update()
            if new_state and new_state != self.state:
                self._change_state(new_state)

    def _render(self) -> None:
        """Renders the active screen onto the virtual surface and
        scales it to the window.

        Draws screen elements onto a fixed-resolution virtual canvas (800x600),
        applies aspect-ratio scaling, and centers (letterboxes)
        the output within the resizable display window.
        """
        self.virtual_screen.fill((0, 0, 0))

        current_screen = self.screens.get(self.state)
        if current_screen:
            current_screen.draw(self.virtual_screen)

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
