import pygame
from typing import Optional, List
from states import GameState
from ui.menus.base_screen import BaseScreen


class MainMenu(BaseScreen):
    """Manages navigation, entry, and the graphical
    interface of the Main Menu."""

    def __init__(self, screen_width: int, screen_height: int):
        super().__init__(screen_width, screen_height)

        self.options: List[str] = [
            "Start Game",
            "View Highscores",
            "Instructions",
            "Exit"
        ]
        self.selected_index: int = 0

        self.title_font = (
            pygame.font.SysFont("emulogic", 32)
            if "emulogic" in pygame.font.get_fonts()
            else pygame.font.SysFont("Arial", 38, bold=True)
        )
        self.option_font = pygame.font.SysFont("Arial", 22, bold=True)
        self.footer_font = pygame.font.SysFont("Arial", 14)

        self.COLOR_BG = (10, 10, 15)
        self.COLOR_TITLE = (255, 255, 0)
        self.COLOR_BORDER = (33, 33, 222)
        self.COLOR_CARD_BG = (15, 15, 25)
        self.COLOR_SELECTED = (255, 183, 255)
        self.COLOR_NORMAL = (200, 200, 210)
        self.COLOR_HIGHLIGHT = (40, 20, 50)

    def handle_event(self, event: pygame.event.Event) -> Optional[GameState]:
        """Processes keyboard navigation."""
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
                    return GameState.HIGHSCORES
                elif selected_option == "Instructions":
                    return GameState.INSTRUCTIONS
                elif selected_option == "Exit":
                    return None

        return GameState.MENU

    def draw(self, surface: pygame.Surface) -> None:
        """Render the main screen."""
        surface.fill(self.COLOR_BG)

        title_surf = self.title_font.render("PAC-MAN 42",
                                            True,
                                            self.COLOR_TITLE)
        title_rect = title_surf.get_rect(center=(self.width // 2, 70))
        surface.blit(title_surf, title_rect)

        line_y = 70
        margin_lines = 40
        pygame.draw.line(surface, self.COLOR_BORDER,
                         (margin_lines, line_y),
                         (title_rect.left - 20, line_y), 3)
        pygame.draw.line(surface, self.COLOR_BORDER,
                         (title_rect.right + 20, line_y),
                         (self.width - margin_lines, line_y), 3)

        card_w, card_h = 440, 260
        card_rect = pygame.Rect((self.width - card_w) // 2,
                                150, card_w, card_h)
        pygame.draw.rect(surface, self.COLOR_CARD_BG,
                         card_rect, border_radius=8)
        pygame.draw.rect(surface, self.COLOR_BORDER,
                         card_rect, width=2, border_radius=8)

        start_y = card_rect.top + 30
        row_height = 50

        for i, option in enumerate(self.options):
            is_selected = (i == self.selected_index)
            option_y = start_y + (i * row_height)
            row_rect = pygame.Rect(card_rect.left + 20,
                                   option_y - 8, card_w - 40, 40)

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

        bar_y = card_rect.bottom + 30
        curr_x = (self.width // 2) - 180
        curr_x += self._draw_key_badge(surface, "W S", curr_x, bar_y) + 6
        curr_x += self._draw_key_badge(surface, "ARROWS", curr_x, bar_y) + 10

        nav_lbl = self.footer_font.render("Navigate", True, (160, 160, 170))
        surface.blit(nav_lbl, (curr_x, bar_y + 2))

        curr_x += nav_lbl.get_width() + 30
        curr_x += self._draw_key_badge(surface, "ENTER", curr_x, bar_y) + 10

        select_lbl = self.footer_font.render("Select", True, (160, 160, 170))
        surface.blit(select_lbl, (curr_x, bar_y + 2))

        info_surf = self.footer_font.render(
            "© 2026 spujol-s/sasanche. All rights reserved.",
            True, (120, 120, 130))
        info_rect = info_surf.get_rect(center=(self.width // 2,
                                               self.height - 25))
        surface.blit(info_surf, info_rect)
