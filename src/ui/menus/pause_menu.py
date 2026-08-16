from typing import List, Optional
import pygame
from src.states import GameState
from src.ui.menus.base_screen import BaseScreen


class PauseMenu(BaseScreen):
    """Graphical user interface and controls for
    the GameState.PAUSED state."""

    def __init__(self, screen_width: int, screen_height: int) -> None:
        super().__init__(screen_width, screen_height)

        self.options: List[str] = ["Resume", "Main Menu", "Exit"]
        self.selected_index: int = 0

        has_emulogic = "emulogic" in pygame.font.get_fonts()
        self.title_font = (
            pygame.font.SysFont("emulogic", 28)
            if has_emulogic
            else pygame.font.SysFont("Arial", 32, bold=True)
        )
        self.option_font = pygame.font.SysFont("Arial", 22, bold=True)
        self.footer_font = pygame.font.SysFont("Arial", 14)

    def handle_event(self, event: pygame.event.Event) -> Optional[GameState]:
        """It handles navigation and option selection in the pause menu."""
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
                selected = self.options[self.selected_index]
                if selected == "Resume":
                    return GameState.PLAYING
                elif selected == "Main Menu":
                    return GameState.MENU
                elif selected == "Exit":
                    return GameState.QUIT

        return GameState.PAUSED

    def draw(self, surface: pygame.Surface) -> None:
        """Render the pause menu."""
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
        start_y = card_rect.top + 35
        row_height = 50

        for i, option in enumerate(self.options):
            is_selected = (i == self.selected_index)
            option_y = start_y + (i * row_height)
            row_rect = pygame.Rect(card_rect.left + 20, option_y - 8,
                                   card_w - 40, 40)

            if is_selected:
                pygame.draw.rect(surface, self.COLOR_HIGHLIGHT,
                                 row_rect, border_radius=6)
                pygame.draw.rect(surface, self.COLOR_SELECTED,
                                 row_rect, width=1, border_radius=6)
                pygame.draw.circle(surface, self.COLOR_TITLE,
                                   (row_rect.left + 25, row_rect.centery), 6)
                color = self.COLOR_SELECTED
            else:
                color = self.COLOR_NORMAL

            opt_surf = self.option_font.render(option, True, color)
            opt_rect = opt_surf.get_rect(center=row_rect.center)
            surface.blit(opt_surf, opt_rect)

        info_surf = self.footer_font.render("Press P or ESC to Resume",
                                            True, (160, 160, 170))
        info_rect = info_surf.get_rect(
            center=(self.width // 2, card_rect.bottom + 35)
        )
        surface.blit(info_surf, info_rect)
