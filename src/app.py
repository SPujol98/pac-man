import sys
import pygame
from states import GameState
from ui.menus import MainMenu, HighscoresMenu, InstructionsMenu
from level_manager.maze_loader import load_maze

'''
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
        self.highscores_menu = HighscoresMenu(self.width, self.height)
        self.instructions_menu = InstructionsMenu(self.width, self.height)

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
            elif self.state == GameState.HIGHSCORES:
                self.state = self.highscores_menu.handle_event(event)

            elif self.state == GameState.INSTRUCTIONS:
                self.state = self.instructions_menu.handle_event(event)

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

        elif self.state == GameState.HIGHSCORES:
            self.highscores_menu.draw(self.screen)
        elif self.state == GameState.INSTRUCTIONS:
            self.instructions_menu.draw(self.screen)
        elif self.state == GameState.PLAYING:
            pass
        pygame.display.flip()'''

"""Orquestador principal con soporte para Superficie Virtual y Escalado."""


class App:
    def __init__(self, config: dict):
        pygame.init()
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

        self.main_menu = MainMenu(self.VIRTUAL_WIDTH,
                                  self.VIRTUAL_HEIGHT)
        self.instructions_menu = InstructionsMenu(self.VIRTUAL_WIDTH,
                                                  self.VIRTUAL_HEIGHT)
        self.highscores_menu = HighscoresMenu(self.VIRTUAL_WIDTH,
                                              self.VIRTUAL_HEIGHT)

        self.state = GameState.MENU
        self.is_running = True

    def run(self) -> None:
        """Bucle principal."""
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

            if self.state == GameState.MENU:
                new_state = self.main_menu.handle_event(event)
                if new_state is None:
                    self.is_running = False
                else:
                    self.state = new_state
            elif self.state == GameState.INSTRUCTIONS:
                self.state = self.instructions_menu.handle_event(event)
            elif self.state == GameState.HIGHSCORES:
                self.state = self.highscores_menu.handle_event(event)

    def _update(self) -> None:
        pass

    def _render(self) -> None:

        self.virtual_screen.fill((0, 0, 0))

        if self.state == GameState.MENU:
            self.main_menu.draw(self.virtual_screen)
        elif self.state == GameState.INSTRUCTIONS:
            self.instructions_menu.draw(self.virtual_screen)
        elif self.state == GameState.HIGHSCORES:
            self.highscores_menu.draw(self.virtual_screen)

        self.screen.fill((0, 0, 0))

        scale_w = self.real_width / self.VIRTUAL_WIDTH
        scale_h = self.real_height / self.VIRTUAL_HEIGHT
        scale = min(scale_w, scale_h)

        scaled_size = (int(self.VIRTUAL_WIDTH * scale),
                       int(self.VIRTUAL_HEIGHT * scale))
        scaled_surface = pygame.transform.scale(self.virtual_screen,
                                                scaled_size)

        pos_x = (self.real_width - scaled_size[0]) // 2
        pos_y = (self.real_height - scaled_size[1]) // 2

        self.screen.blit(scaled_surface, (pos_x, pos_y))
        pygame.display.flip()
