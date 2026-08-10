import pygame
from typing import Optional, List
from states import GameState


class MainMenu:
    """Manages the logic, keyboard navigation,
    and rendering of the Main Menu"""
    def __init__(self, screen_width: int, screen_height: int):
        self.width = screen_width
        self.height = screen_height

        self.options: List[str] = ["Start Game",
                                   "View Highscores",
                                   "Instructions",
                                   "Exit"]
        self.selected_index: int = 0

        self.title_font = (
            pygame.font.SysFont("emulogic", 48)
            if "emulogic" in pygame.font.get_fonts()
            else pygame.font.SysFont("Arial", 48, bold=True)
        )
        self.option_font = pygame.font.SysFont("Arial", 28, bold=True)

        self.COLOR_TITLE = (255, 255, 0)
        self.COLOR_SELECTED = (255, 183, 255)
        self.COLOR_NORMAL = (255, 255, 255)
        self.COLOR_BG = (0, 0, 0)

    def handle_event(self, event: pygame.event.Event) -> Optional[GameState]:
        """Use the arrow keys to navigate the menu.
        Returns:
            The new GameState if the user selects an option,
            or None if no change is made.
        """
        if event.type == pygame.KEYDOWN:

            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (
                    (self.selected_index - 1) % len(self.options)
                    )
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (
                    (self.selected_index + 1) % len(self.options)
                    )
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):

                selected_option = self.options[self.selected_index]
                if selected_option == "Start Game":
                    return GameState.PLAYING
                elif selected_option == "View Highscores":
                    print("Sección de Highscores en construcción")
                    return GameState.HIGHSCORES
                elif selected_option == "Instructions":
                    print("Sección de Instrucciones en construcción")
                    return GameState.INSTRUCTIONS
                elif selected_option == "Exit":
                    return None
        return GameState.MENU

    def draw(self, surface: pygame.Surface) -> None:
        """Render the main menu on the specified surface."""
        surface.fill(self.COLOR_BG)

        title_text = "PAC-MAN 42"
        title_surf = self.title_font.render(title_text, True, self.COLOR_TITLE)
        title_rect = title_surf.get_rect(center=(self.width // 2,
                                                 self.height // 4))
        surface.blit(title_surf, title_rect)

        start_y = self.height // 2
        for i, option in enumerate(self.options):
            is_selected = (i == self.selected_index)
            color = self.COLOR_SELECTED if is_selected else self.COLOR_NORMAL

            prefix = "> " if is_selected else "  "
            opt_surf = self.option_font.render(f"{prefix}{option}",
                                               True, color)
            opt_rect = opt_surf.get_rect(center=(self.width // 2,
                                                 start_y + i * 50))
            surface.blit(opt_surf, opt_rect)

        info_font = pygame.font.SysFont("Arial", 24)
        info_surf = info_font.render(
            "© 2026 spujol-s/sasanche. All rights reserved.",
            True,
            (150, 150, 150))
        info_rect = info_surf.get_rect(center=(self.width // 2,
                                               self.height - 40))
        surface.blit(info_surf, info_rect)
