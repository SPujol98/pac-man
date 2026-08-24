from typing import Optional
import pygame
from src.states import GameState
from src.ui.menus.base_screen import BaseScreen
from src.systems.highscore import save_highscore


class BaseScoreEntryScreen(BaseScreen):
    """Base end-game screen with a text box for entering the player name."""

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        title: str,
        title_color: tuple[int, int, int],
        subtitle: str = "",
        highscore_file: str = "highscores.json",
    ) -> None:
        super().__init__(screen_width, screen_height)

        self.title_text = title
        self.title_color = title_color
        self.subtitle_text = subtitle
        self.highscore_file = highscore_file

        self.final_score: int = 0
        self.player_name: str = ""
        self.max_name_length: int = 10

        self.title_font = self._load_arcade_font(26, 30)
        self.subtitle_font = pygame.font.SysFont("Arial", 16)
        self.score_font = pygame.font.SysFont("Arial", 22, bold=True)
        self.input_font = pygame.font.SysFont("Arial", 24, bold=True)
        self.footer_font = pygame.font.SysFont("Arial", 14)

    def set_final_score(self, score: int) -> None:
        """Set the final score and reset the name entry field."""
        self.final_score = score
        self.player_name = ""

    def handle_event(self, event: pygame.event.Event) -> Optional[GameState]:
        """Handle text input and confirm the name with Enter."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]

            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                name_to_save = self.player_name.strip() or "AAA"
                self._save_highscore(name_to_save, self.final_score)
                return GameState.HIGHSCORES

            else:
                if len(self.player_name) < self.max_name_length:
                    char = event.unicode.upper()
                    if char.isalnum() or char == " ":
                        self.player_name += char

        return None

    def draw(self, surface: pygame.Surface) -> None:
        """Render the retro-style score entry interface."""
        surface.fill(self.COLOR_BG)

        self._draw_glow_text(surface, self.title_text, self.title_font,
                             self.title_color, (self.width // 2, 70),
                             self.title_color, glow_alpha=55)

        if self.subtitle_text:
            sub_surf = self.subtitle_font.render(self.subtitle_text,
                                                 True, self.COLOR_NORMAL)
            sub_rect = sub_surf.get_rect(center=(self.width // 2, 110))
            surface.blit(sub_surf, sub_rect)

        card_w, card_h = 420, 240
        card_rect = pygame.Rect((self.width - card_w) // 2,
                                140, card_w, card_h)
        pygame.draw.rect(surface, self.COLOR_CARD_BG,
                         card_rect, border_radius=8)
        pygame.draw.rect(surface, self.COLOR_BORDER,
                         card_rect, width=2, border_radius=8)

        score_str = f"FINAL SCORE: {self.final_score:05d}"
        score_surf = self.score_font.render(score_str,
                                            True, self.COLOR_TITLE)
        score_rect = score_surf.get_rect(center=(self.width // 2,
                                                 card_rect.top + 45))
        surface.blit(score_surf, score_rect)

        prompt_surf = self.subtitle_font.render("ENTER YOUR NAME:",
                                                True, self.COLOR_LABEL)
        prompt_rect = prompt_surf.get_rect(center=(self.width // 2,
                                                   card_rect.top + 100))
        surface.blit(prompt_surf, prompt_rect)

        input_box = pygame.Rect(card_rect.left + 50,
                                card_rect.top + 125, card_w - 100, 45)
        pygame.draw.rect(surface, self.COLOR_HIGHLIGHT,
                         input_box, border_radius=6)
        pygame.draw.rect(surface, self.COLOR_SELECTED,
                         input_box, width=1, border_radius=6)

        show_cursor = (pygame.time.get_ticks() // 500) % 2 == 0
        display_text = self.player_name + ("_" if show_cursor else " ")

        text_surf = self.input_font.render(display_text,
                                           True, self.COLOR_SELECTED)
        text_rect = text_surf.get_rect(center=input_box.center)
        surface.blit(text_surf, text_rect)

        if (pygame.time.get_ticks() // 400) % 2 == 0:
            footer_surf = self.footer_font.render(
                "PRESS ENTER TO SAVE SCORE",
                True, self.COLOR_HEADER)
            footer_rect = footer_surf.get_rect(
                center=(self.width // 2,
                        card_rect.bottom + 35)
            )
            surface.blit(footer_surf, footer_rect)

    def _save_highscore(self, name: str, score: int) -> None:
        """Persist the entry through the highscore system."""
        save_highscore(name=name, score=score, filepath=self.highscore_file)
