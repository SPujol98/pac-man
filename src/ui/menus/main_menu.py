import pygame
from typing import List, Optional, Tuple
from src.states import GameState
from src.systems.highscore import load_highscores
from src.ui import sprites
from src.ui.menus.base_screen import BaseScreen


class MainMenu(BaseScreen):
    """Main menu screen with entry navigation to game, scores, and help."""

    CHASE_SPRITES = ("blinky", "pinky", "inky", "clyde")

    def __init__(self, screen_width: int, screen_height: int,
                 highscore_file: str = "highscores.json") -> None:
        super().__init__(screen_width, screen_height)

        self.highscore_file = highscore_file
        self.top_score: int = 0

        self.options: List[Tuple[str, GameState]] = [
            ("Start Game", GameState.PLAYING),
            ("View Highscores", GameState.HIGHSCORES),
            ("Instructions", GameState.INSTRUCTIONS),
            ("Exit", GameState.QUIT)
        ]
        self.selected_index: int = 0

        self.title_font = self._load_arcade_font(32, 38)
        self.option_font = pygame.font.SysFont("Arial", 22, bold=True)
        self.footer_font = pygame.font.SysFont("Arial", 14)
        self.score_font = self._load_arcade_font(14, 16)

    def on_enter(self, previous_state: GameState) -> None:
        """Refresh the arcade HIGH SCORE header from storage."""
        scores = load_highscores(self.highscore_file)
        self.top_score = scores[0]["score"] if scores else 0

    def handle_event(self, event: pygame.event.Event) -> Optional[GameState]:
        """Process keyboard navigation and option selection."""
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
                return self.options[self.selected_index][1]
        return GameState.MENU

    def _draw_high_score_header(self, surface: pygame.Surface) -> None:
        """Draw the arcade-style top score banner at the top."""
        label = self.footer_font.render("HIGH SCORE",
                                        True, self.COLOR_HEADER)
        value = self.score_font.render(f"{self.top_score:05d}",
                                       True, self.COLOR_TITLE)
        surface.blit(label, label.get_rect(
            center=(self.width // 2 - 52, 18)))
        surface.blit(value, value.get_rect(
            center=(self.width // 2 + 48, 18)))

    def _draw_chase_strip(self, surface: pygame.Surface) -> None:
        """Draw the animated Pac-Man chase across the bottom of the menu."""
        size = 26
        y = 495
        ticks = pygame.time.get_ticks()
        span = self.width + 260
        lead_x = (ticks * 0.13) % span - 130

        frames = sprites.try_get_pacman_frames(size)
        if frames is not None:
            sequence = (0, 1, 2, 1)
            frame = frames[sequence[(ticks // 90) % 4]]
            surface.blit(frame, (int(lead_x), y))

        for i, key in enumerate(self.CHASE_SPRITES):
            ghost = sprites.try_get_sprite(key, size)
            if ghost is not None:
                bob = 2 if (ticks // 200 + i) % 2 == 0 else 0
                surface.blit(ghost, (int(lead_x) - 55 - (i * 45), y + bob))

    def draw(self, surface: pygame.Surface) -> None:
        """Render the main menu screen."""
        surface.fill(self.COLOR_BG)

        self._draw_high_score_header(surface)
        self._draw_glow_text(surface, "PAC-MAN 42", self.title_font,
                             self.COLOR_TITLE, (self.width // 2, 78),
                             self.COLOR_HEADER, glow_alpha=70)

        line_y = 78
        margin_lines = 40
        title_rect = self.title_font.size("PAC-MAN 42")
        title_half = title_rect[0] // 2
        pygame.draw.line(surface, self.COLOR_BORDER,
                         (margin_lines, line_y),
                         (self.width // 2 - title_half - 20, line_y), 3)
        pygame.draw.line(surface, self.COLOR_BORDER,
                         (self.width // 2 + title_half + 20, line_y),
                         (self.width - margin_lines, line_y), 3)

        card_w, card_h = 440, 260
        card_rect = pygame.Rect((self.width - card_w) // 2,
                                150, card_w, card_h)
        pygame.draw.rect(surface, self.COLOR_CARD_BG,
                         card_rect, border_radius=8)
        pygame.draw.rect(surface, self.COLOR_BORDER,
                         card_rect, width=2, border_radius=8)

        self._draw_option_list(surface, self.options, self.selected_index,
                               card_rect, self.option_font)

        bar_y = card_rect.bottom + 30
        curr_x = (self.width // 2) - 180
        curr_x += self._draw_key_badge(surface, "W S", curr_x, bar_y) + 6
        curr_x += self._draw_key_badge(surface, "ARROWS", curr_x, bar_y) + 10

        nav_lbl = self.footer_font.render("Navigate", True, self.COLOR_LABEL)
        surface.blit(nav_lbl, (curr_x, bar_y + 2))

        curr_x += nav_lbl.get_width() + 30
        curr_x += self._draw_key_badge(surface, "ENTER", curr_x, bar_y) + 10

        select_lbl = self.footer_font.render("Select", True, self.COLOR_LABEL)
        surface.blit(select_lbl, (curr_x, bar_y + 2))

        self._draw_chase_strip(surface)

        info_surf = self.footer_font.render(
            "© 2026 spujol-s/sasanche. All rights reserved.",
            True, (120, 115, 150))
        info_rect = info_surf.get_rect(center=(self.width // 2,
                                               self.height - 25))
        surface.blit(info_surf, info_rect)
