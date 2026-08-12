import math
import pygame


class HUD:
    """Controls the display of the top panel during gameplay."""

    def __init__(self, screen_width: int, screen_height: int):
        self.width = screen_width
        self.height = screen_height

        self.hud_height = 45

        self.font_label = pygame.font.SysFont("Arial", 12, bold=True)
        self.font_value = (
            pygame.font.SysFont("emulogic", 16)
            if "emulogic" in pygame.font.get_fonts()
            else pygame.font.SysFont("Arial", 18, bold=True)
        )

        self.COLOR_BG = (10, 10, 15)
        self.COLOR_BORDER = (33, 33, 222)
        self.COLOR_LABEL = (180, 180, 190)
        self.COLOR_SCORE = (255, 255, 255)
        self.COLOR_TIME_NORMAL = (0, 255, 255)
        self.COLOR_TIME_WARN = (255, 50, 50)
        self.COLOR_LEVEL = (255, 183, 255)
        self.COLOR_PACMAN = (255, 255, 0)

    def _draw_life_icon(self, surface: pygame.Surface, x: int, y: int, radius: int = 8) -> None:
        """Draw a procedural Pac-Man icon with its mouth open and pointing to the left."""

        pygame.draw.circle(surface, self.COLOR_PACMAN, (x, y), radius)


        mouth_pts = [
            (x, y),
            (x - radius - 1, y - (radius // 2)),
            (x - radius - 1, y + (radius // 2)),
        ]
        pygame.draw.polygon(surface, self.COLOR_BG, mouth_pts)

    def draw(
        self,
        surface: pygame.Surface,
        score: int,
        lives: int,
        level: int,
        time_remaining: int
    ) -> None:
        """Render the top bar of the HUD with the 4 requested indicators."""

        hud_rect = pygame.Rect(0, 0, self.width, self.hud_height)
        pygame.draw.rect(surface, self.COLOR_BG, hud_rect)
        pygame.draw.line(surface, self.COLOR_BORDER, (0, self.hud_height), (self.width, self.hud_height), 2)

        padding_x = 30
        section_width = (self.width - (padding_x * 2)) // 4

        x_score = padding_x
        lbl_score = self.font_label.render("SCORE", True, self.COLOR_LABEL)
        val_score = self.font_value.render(f"{score:05d}", True, self.COLOR_SCORE)

        surface.blit(lbl_score, (x_score, 4))
        surface.blit(val_score, (x_score, 18))

        x_time = padding_x + section_width
        time_color = self.COLOR_TIME_WARN if time_remaining <= 10 else self.COLOR_TIME_NORMAL

        lbl_time = self.font_label.render("TIME", True, self.COLOR_LABEL)
        val_time = self.font_value.render(f"{max(0, time_remaining):02d}s", True, time_color)

        surface.blit(lbl_time, (x_time, 4))
        surface.blit(val_time, (x_time, 18))

        x_level = padding_x + (section_width * 2)
        lbl_level = self.font_label.render("LEVEL", True, self.COLOR_LABEL)
        val_level = self.font_value.render(f"{level:02d}", True, self.COLOR_LEVEL)

        surface.blit(lbl_level, (x_level, 4))
        surface.blit(val_level, (x_level, 18))

        x_lives = padding_x + (section_width * 3)
        lbl_lives = self.font_label.render("LIVES", True, self.COLOR_LABEL)
        surface.blit(lbl_lives, (x_lives, 4))

        icon_start_x = x_lives + 10
        icon_y = 28
        for i in range(max(0, lives)):
            self._draw_life_icon(surface, icon_start_x + (i * 22), icon_y, radius=8)