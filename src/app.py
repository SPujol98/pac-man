import sys
import pygame
from states import GameState
from ui.menus import MainMenu
from level_manager.maze_loader import load_maze

# hay que recordar implmentar el control de keyboardinterrupt
class App:
    def __init__(self, config: dict):
        pygame.init()
        self.config = config

        window_cfg = config.get("window", {})
        self.width = window_cfg.get("width", 800)
        self.height = window_cfg.get("height", 600)
        self.fps = window_cfg.get("fps", 60)

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Pac-Man 42")
        self.clock = pygame.time.Clock()

        self.main_menu = MainMenu(self.width, self.height)

        self.state = GameState.MENU
        self.is_running = True
        

        self.maze_data = load_maze(
            width=config.get("maze", {}).get("width", 21),
            height=config.get("maze", {}).get("height", 21),
            seed=config.get("maze", {}).get("seed", 42),
        )

    def run(self):
        """Main game loop."""
        while self.is_running:
            self._handle_events()
            self._update()
            self._render()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            if self.state == GameState.MENU:
                new_state = self.main_menu.handle_event(event)
                if new_state is None:
                    self.is_running = False
                else:
                    self.state = new_state

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.state == GameState.PLAYING:
                    self.state = GameState.PAUSED
                elif self.state == GameState.PAUSED:
                    self.state = GameState.PLAYING

    def _update(self):
        pass

    def _render(self):
        if self.state == GameState.MENU:
            self.main_menu.draw(self.screen)

        elif self.state == GameState.PLAYING:
            pass
        pygame.display.flip()