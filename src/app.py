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

        self.screens: dict[GameState, BaseScreen] = {
            GameState.MENU: MainMenu(self.VIRTUAL_WIDTH, self.VIRTUAL_HEIGHT),
            GameState.INSTRUCTIONS: InstructionsMenu(self.VIRTUAL_WIDTH,
                                                     self.VIRTUAL_HEIGHT),
            GameState.HIGHSCORES: HighscoresMenu(self.VIRTUAL_WIDTH,
                                                 self.VIRTUAL_HEIGHT),
            GameState.PLAYING: PlayScreen(self.VIRTUAL_WIDTH,
                                          self.VIRTUAL_HEIGHT,
                                          self.config),
            GameState.PAUSED: PauseMenu(self.VIRTUAL_WIDTH,
                                        self.VIRTUAL_HEIGHT),
            GameState.GAME_OVER: GameOverScreen(self.VIRTUAL_WIDTH,
                                                self.VIRTUAL_HEIGHT),
            GameState.WIN: WinScreen(self.VIRTUAL_WIDTH,
                                     self.VIRTUAL_HEIGHT),
        }

    def run(self) -> None:
        """Main execution loop."""
        while self.is_running:
            self._handle_events()
            self._update()
            self._render()
            self.clock.tick(self.fps)
        pygame.quit()

    def _change_state(self, new_state: GameState) -> None:
        """Cambia el estado actual e inyecta la puntuación
        si es pantalla final."""
        if new_state == GameState.QUIT:
            self.is_running = False
        if new_state in (GameState.GAME_OVER, GameState.WIN):
            play_screen = self.screens.get(GameState.PLAYING)
            target_screen = self.screens.get(new_state)

            if play_screen and hasattr(target_screen, "set_final_score"):
                final_score = getattr(play_screen, "game", None)
                score_val = final_score.score if final_score else 0
                target_screen.set_final_score(score_val)
        self.state = new_state

    def _handle_events(self) -> None:
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
        current_screen = self.screens.get(self.state)
        if current_screen:
            new_state = current_screen.update()
            if new_state and new_state != self.state:
                self._change_state(new_state)

    def _render(self) -> None:
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

    '''
    def run(self) -> None:
        """Main execution loop."""
        while self.is_running:
            self._handle_events()
            self._update()
            self._render()
            self.clock.tick(self.fps)

    def _change_state(self, new_state: GameState) -> None:
        """Centraliza la transición de estados y la transferencia de datos."""
        if new_state in (GameState.GAME_OVER, GameState.WIN):
            play_screen = self.screens.get(GameState.PLAYING)
            target_screen = self.screens.get(new_state)

            if play_screen and hasattr(target_screen, "set_final_score"):
                final_score = play_screen.game.score
                target_screen.set_final_score(final_score)
        self.state = new_state

    def _handle_events(self) -> None:
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
                    if new_state is None:
                        self.is_running = False
                    elif new_state != self.state:
                        self._change_state(new_state)

    def _update(self) -> None:
        """Actualiza la lógica de la pantalla actual y
        procesa cambios de estado."""
        current_screen = self.screens.get(self.state)
        if current_screen:
            new_state = current_screen.update()
            if new_state is None:
                self.is_running = False
            elif new_state and new_state != self.state:
                self._change_state(new_state)'''
