import sys
import pygame
from src.states import GameState
from src.ui.menus import MainMenu, HighscoresMenu, InstructionsMenu, BaseScreen
from src.ui.play_screen import PlayScreen
from src.level_manager.maze_loader import load_maze


class App:
    def __init__(self, config: dict):
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
        self.real_width = window_cfg.get("width", 800)
        self.real_height = window_cfg.get("height", 600)
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
        }

    def run(self) -> None:
        """Main execution loop."""
        while self.is_running:
            self._handle_events()
            self._update()
            self._render()
            self.clock.tick(self.fps)

        pygame.quit()
        sys.exit()

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
                        self.state = new_state

    def _update(self) -> None:

        current_screen = self.screens.get(self.state)
        if current_screen:
            current_screen.update()

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
