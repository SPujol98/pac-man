from typing import List, Dict, Any, Optional
import pygame
from src.states import GameState
from src.ui.menus.base_screen import BaseScreen
from src.systems.highscore import load_highscores


class HighscoresMenu(BaseScreen):
    """Display the high scores table (Top 10)."""

    def __init__(self,
                 screen_width: int,
                 screen_height: int,
                 highscore_file: str = "highscores.json") -> None:
        super().__init__(screen_width, screen_height)
        self.highscore_file = highscore_file
        self.scores: List[Dict[str, Any]] = []

        has_emulogic = "emulogic" in pygame.font.get_fonts()
        self.title_font = (
            pygame.font.SysFont("emulogic", 26)
            if has_emulogic
            else pygame.font.SysFont("Arial", 30, bold=True)
        )
        self.header_font = pygame.font.SysFont("Arial", 18, bold=True)
        self.row_font = pygame.font.SysFont("Arial", 18, bold=True)
        self.footer_font = pygame.font.SysFont("Arial", 14)

    def refresh_scores(self) -> None:
        """Load the updated scores from storage."""
        self.scores = load_highscores(self.highscore_file)

    def handle_event(self, event: pygame.event.Event) -> Optional[GameState]:
        """Press ESC, Enter, or the Space bar to return to the main menu."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                return GameState.MENU

        return GameState.HIGHSCORES

    def draw(self, surface: pygame.Surface) -> None:
        """Render the retro leaderboard."""
        self.refresh_scores()

        surface.fill(self.COLOR_BG)

        title_surf = self.title_font.render("HIGH SCORES",
                                            True,
                                            self.COLOR_TITLE)
        title_rect = title_surf.get_rect(center=(self.width // 2, 55))
        surface.blit(title_surf, title_rect)

        card_w, card_h = 480, 430
        card_rect = pygame.Rect((self.width - card_w) // 2, 95, card_w, card_h)
        pygame.draw.rect(surface,
                         self.COLOR_CARD_BG,
                         card_rect,
                         border_radius=8)
        pygame.draw.rect(surface,
                         self.COLOR_BORDER,
                         card_rect, width=2,
                         border_radius=8)

        rank_hdr = self.header_font.render("RANK", True, self.COLOR_SELECTED)
        name_hdr = self.header_font.render("NAME", True, self.COLOR_SELECTED)
        score_hdr = self.header_font.render("SCORE", True, self.COLOR_SELECTED)

        header_y = card_rect.top + 20
        surface.blit(rank_hdr, (card_rect.left + 35, header_y))
        surface.blit(name_hdr, (card_rect.left + 160, header_y))
        surface.blit(score_hdr, (card_rect.right - 130, header_y))

        line_y = header_y + 28
        pygame.draw.line(
            surface,
            self.COLOR_BORDER,
            (card_rect.left + 20, line_y),
            (card_rect.right - 20, line_y),
            width=1,
        )
        if not self.scores:
            empty_surf = self.row_font.render("NO HIGH SCORES YET",
                                              True,
                                              self.COLOR_NORMAL)
            empty_rect = empty_surf.get_rect(
                center=(self.width // 2, card_rect.top + 200))
            surface.blit(empty_surf, empty_rect)
        else:
            start_y = line_y + 15
            row_height = 32

            for i in range(min(10, len(self.scores))):
                entry = self.scores[i]
                y_pos = start_y + (i * row_height)

                rank_str = f"{i + 1:2d}."
                name_str = entry.get("name", "AAA")
                score_str = f"{entry.get('score', 0):05d}"

                color = self.COLOR_TITLE if i < 3 else self.COLOR_NORMAL

                r_surf = self.row_font.render(rank_str, True, color)
                n_surf = self.row_font.render(name_str, True, color)
                s_surf = self.row_font.render(score_str, True, color)

                surface.blit(r_surf, (card_rect.left + 40, y_pos))
                surface.blit(n_surf, (card_rect.left + 160, y_pos))
                surface.blit(s_surf, (card_rect.right - 125, y_pos))

        footer_surf = self.footer_font.render(
            "PRESS ESC OR ENTER FOR MAIN MENU", True, self.COLOR_LABEL
        )
        footer_rect = footer_surf.get_rect(
            center=(self.width // 2, card_rect.bottom + 30))
        surface.blit(footer_surf, footer_rect)
