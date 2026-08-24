from typing import List, Optional, Tuple
import pygame
from src.states import GameState
from src.ui.menus.base_screen import BaseScreen


class PauseMenu(BaseScreen):
    """Pause menu screen shown while the game is suspended."""

    def __init__(self, screen_width: int, screen_height: int) -> None:
        super().__init__(screen_width, screen_height)

        self.options: List[Tuple[str, GameState]] = [
            ("Resume", GameState.PLAYING),
            ("Main Menu", GameState.MENU),
            ("Exit", GameState.QUIT)
        ]
        self.selected_index: int = 0

        self.title_font = self._load_arcade_font(28, 32)
        self.option_font = pygame.font.SysFont("Arial", 22, bold=True)
        self.footer_font = pygame.font.SysFont("Arial", 14)

    def handle_event(self, event: pygame.event.Event) -> Optional[GameState]:
        """Process navigation, resume shortcut, and option selection."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_p, pygame.K_ESCAPE):
                return GameState.PLAYING

            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (
                    (self.selected_index - 1) % len(self.options)
                )
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (
                    (self.selected_index + 1) % len(self.options)
                )
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.options[self.selected_index][1]

        return GameState.PAUSED

    def draw(self, surface: pygame.Surface) -> None:
        """Render the pause menu screen."""
        surface.fill(self.COLOR_BG)
        title_surf = self.title_font.render("PAUSED", True, self.COLOR_TITLE)
        title_rect = title_surf.get_rect(center=(self.width // 2, 110))
        surface.blit(title_surf, title_rect)

        card_w, card_h = 380, 220
        card_rect = pygame.Rect((self.width - card_w) // 2, 170,
                                card_w, card_h)
        pygame.draw.rect(surface, self.COLOR_CARD_BG,
                         card_rect, border_radius=8)
        pygame.draw.rect(surface, self.COLOR_BORDER,
                         card_rect, width=2, border_radius=8)

        self._draw_option_list(surface, self.options, self.selected_index,
                               card_rect, self.option_font, start_offset=35)

        info_surf = self.footer_font.render("Press P or ESC to Resume",
                                            True, (160, 160, 170))
        info_rect = info_surf.get_rect(
            center=(self.width // 2, card_rect.bottom + 35)
        )
        surface.blit(info_surf, info_rect)
