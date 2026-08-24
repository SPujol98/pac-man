from abc import ABC, abstractmethod
from typing import Optional, Sequence, Tuple
import pygame
from src.states import GameState


class BaseScreen(ABC):
    """Abstract common interface and shared drawing tools for all screens."""

    COLOR_BG = (10, 7, 22)
    COLOR_LABEL = (150, 140, 180)
    COLOR_TEXT = (255, 255, 255)
    COLOR_TEXT1 = (220, 218, 235)
    COLOR_TITLE = (255, 255, 0)
    COLOR_BORDER = (0, 229, 255)
    COLOR_HEADER = (255, 110, 220)
    COLOR_DOT = (255, 183, 82)
    COLOR_CARD_BG = (18, 13, 36)
    COLOR_SELECTED = (255, 110, 220)
    COLOR_NORMAL = (205, 200, 225)
    COLOR_HIGHLIGHT = (45, 15, 55)
    COLOR_KEY_BG = (30, 22, 55)
    COLOR_KEY_BORDER = (0, 229, 255)

    def __init__(self, screen_width: int, screen_height: int):
        self.width = screen_width
        self.height = screen_height

        if not pygame.font.get_init():
            pygame.font.init()

        self.key_font = pygame.font.SysFont("Arial", 12, bold=True)

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> Optional[GameState]:
        """Process native Pygame keyboard input."""
        pass

    def update(self) -> Optional[GameState]:
        """Update the screen's internal logic or animation (optional)."""
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the graphic content on the indicated surface."""
        pass

    def on_enter(self, previous_state: GameState) -> None:
        """Optional hook that runs every time this screen is entered."""
        pass

    def _load_arcade_font(self, size: int,
                          fallback_size: int) -> pygame.font.Font:
        """Return the emulogic arcade font if installed, else bold Arial."""
        if "emulogic" in pygame.font.get_fonts():
            return pygame.font.SysFont("emulogic", size)
        return pygame.font.SysFont("Arial", fallback_size, bold=True)

    def _draw_glow_text(self, surface: pygame.Surface, text: str,
                        font: pygame.font.Font,
                        color: Tuple[int, int, int],
                        center: Tuple[int, int],
                        glow_color: Tuple[int, int, int],
                        glow_alpha: int = 60) -> None:
        """Render text with a soft neon halo behind it."""
        text_surf = font.render(text, True, color)
        glow_surf = font.render(text, True, glow_color)
        glow_surf.set_alpha(glow_alpha)

        w, h = text_surf.get_size()
        for scale in (1.25, 1.10):
            halo = pygame.transform.smoothscale(
                glow_surf, (int(w * scale), int(h * scale)))
            halo.set_alpha(glow_alpha)
            surface.blit(halo, halo.get_rect(center=center))

        surface.blit(text_surf, text_surf.get_rect(center=center))

    def _draw_option_list(
            self,
            surface: pygame.Surface,
            options: Sequence[Tuple[str, GameState]],
            selected_index: int,
            card_rect: pygame.Rect,
            font: pygame.font.Font,
            start_offset: int = 30,
            row_height: int = 50) -> None:
        """Render a vertical selectable option list inside a card."""
        for i, (label, _) in enumerate(options):
            is_selected = (i == selected_index)
            option_y = card_rect.top + start_offset + (i * row_height)
            row_rect = pygame.Rect(card_rect.left + 20,
                                   option_y - 8, card_rect.width - 40, 40)

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

            opt_surf = font.render(label, True, color)
            opt_rect = opt_surf.get_rect(center=row_rect.center)
            surface.blit(opt_surf, opt_rect)

    def _draw_key_badge(self,
                        surface: pygame.Surface,
                        text: str,
                        x: int,
                        y: int) -> int:
        """Draw an arcade-style key badge and return its width."""
        text_surf = self.key_font.render(text, True, (255, 255, 255))
        padding_x, padding_y = 6, 3
        width = text_surf.get_width() + (padding_x * 2)
        height = text_surf.get_height() + (padding_y * 2)

        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, (0, 0, 0), rect.move(2, 2), border_radius=4)
        pygame.draw.rect(surface, self.COLOR_KEY_BG, rect, border_radius=4)
        pygame.draw.rect(surface, self.COLOR_KEY_BORDER, rect,
                         width=1, border_radius=4)

        surface.blit(text_surf, (x + padding_x, y + padding_y))
        return width
