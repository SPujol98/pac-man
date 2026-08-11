import pygame
from typing import Optional
from states import GameState
from ui.menus.base_screen import BaseScreen
from ui.renderer import Renderer
from ui.hud import HUD
from ui.input_handler import InputHandler


class PlayScreen(BaseScreen):
    """Manages the game's lifecycle when the state is GameState.PLAYING."""

    def __init__(self, screen_width: int, screen_height: int, maze_data: dict):
        super().__init__(screen_width, screen_height)

        self.maze_data = maze_data

        self.input_handler = InputHandler()
        self.renderer = Renderer(screen_width, screen_height)
        self.hud = HUD(screen_width, screen_height)

        self.score: int = 0
        self.lives: int = 3
        self.level: int = 1
        self.time_remaining: int = 90

    def handle_event(self, event: pygame.event.Event) -> Optional[GameState]:
        """Processes input during gameplay (movement and pause)."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                return GameState.PAUSED
            self.input_handler.process_event(event)

        return GameState.PLAYING

    def update(self) -> None:
        """Updates the positions and logic of the game entities."""
        # TODO: Aquí llamaremos a la lógica de movimiento de Pac-Man y los fantasmas
        pass

    def draw(self, surface: pygame.Surface) -> None:
        """Render the maze, entities, and HUD on the virtual canvas."""
        surface.fill((0, 0, 0))

        grid = self.maze_data.grid
        self.renderer.draw_maze(surface, grid)

        self.hud.draw(
            surface=surface,
            score=self.score,
            lives=self.lives,
            level=self.level,
            time_remaining=self.time_remaining
        )