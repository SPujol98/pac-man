import pygame


class HUD:
    """Renders and manages the top Heads-Up Display (HUD) bar
    in an arcade style.

    Displays real-time gameplay indicators including current score,
    remaining level time, active level number, and player lives represented
    by procedural Pac-Man icons.
    """

    def __init__(self, screen_width: int, screen_height: int) -> None:
        """Initializes the HUD layout dimensions, font assets,
        and visual color palette.

        Args:
            screen_width: Width of the display surface in pixels.
            screen_height: Height of the display surface in pixels.
        """
        self.width = screen_width
        self.height = screen_height
        self.hud_height = 45

        has_emulogic = "emulogic" in pygame.font.get_fonts()
        self.font_label = pygame.font.SysFont("Arial", 11, bold=True)
        self.font_value = (
            pygame.font.SysFont("emulogic", 14)
            if has_emulogic
            else pygame.font.SysFont("Arial", 16, bold=True)
        )

        self.COLOR_BG = (10, 10, 15)
        self.COLOR_CARD_BG = (15, 15, 25)
        self.COLOR_BORDER = (33, 33, 222)
        self.COLOR_LABEL = (160, 160, 170)
        self.COLOR_SCORE = (255, 255, 255)
        self.COLOR_TIME_NORMAL = (0, 255, 255)
        self.COLOR_TIME_WARN = (255, 50, 50)
        self.COLOR_LEVEL = (255, 183, 255)
        self.COLOR_PACMAN = (255, 255, 0)

    def _draw_life_icon(self, surface: pygame.Surface, x: int,
                        is_invincible: bool, y: int, radius: int = 7) -> None:
        """Draws a single procedural Pac-Man icon representing
        an available life.

        Renders a circle with a cut-out wedge polygon to simulate an
        open mouth, applying either standard yellow or dynamic
        invincibility coloring.

        Args:
            surface: The Pygame target surface to draw onto.
            x: The horizontal center position of the icon in pixels.
            is_invincible: Flag indicating whether to apply a
                           cycling rainbow color.
            y: The vertical center position of the icon in pixels.
            radius: Radius of the Pac-Man icon circle in pixels.
                    Defaults to 7.
        """
        if is_invincible:
            pygame.draw.circle(surface, self.get_invincible_color(),
                               (x, y), radius)
        else:
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
        time_remaining: int,
        invincible: bool
    ) -> None:
        """Renders the complete top HUD bar with all stats, labels, and icons.

        Divides the top bar into 4 distinct sections
        (Score, Time, Level, Lives) and draws text textures and life icons
        onto the target surface.

        Args:
            surface: The main Pygame display surface to draw onto.
            score: Current player score value.
            lives: Number of remaining player lives.
            level: Active level sequence number.
            time_remaining: Remaining level time in seconds.
            invincible: Whether player invincibility mode is currently active.
        """

        hud_rect = pygame.Rect(0, 0, self.width, self.hud_height)
        pygame.draw.rect(surface, self.COLOR_BG, hud_rect)
        pygame.draw.line(
            surface,
            self.COLOR_BORDER,
            (0, self.hud_height),
            (self.width, self.hud_height),
            2
        )

        padding_x = 25
        section_w = (self.width - (padding_x * 2)) // 4

        x_score = padding_x
        lbl_score = self.font_label.render("SCORE", True, self.COLOR_LABEL)
        val_score = self.font_value.render(f"{score:05d}",
                                           True, self.COLOR_SCORE)

        surface.blit(lbl_score, (x_score, 4))
        surface.blit(val_score, (x_score, 18))

        x_time = padding_x + section_w
        time_color = (self.COLOR_TIME_WARN if time_remaining <= 10
                      else self.COLOR_TIME_NORMAL)

        lbl_time = self.font_label.render("TIME", True, self.COLOR_LABEL)
        val_time = self.font_value.render(f"{max(0, time_remaining):02d}s",
                                          True, time_color)

        surface.blit(lbl_time, (x_time, 4))
        surface.blit(val_time, (x_time, 18))

        x_level = padding_x + (section_w * 2)
        lbl_level = self.font_label.render("LEVEL", True, self.COLOR_LABEL)
        val_level = self.font_value.render(f"{level:02d}",
                                           True, self.COLOR_LEVEL)

        surface.blit(lbl_level, (x_level, 4))
        surface.blit(val_level, (x_level, 18))

        x_lives = padding_x + (section_w * 3)
        lbl_lives = self.font_label.render("LIVES", True, self.COLOR_LABEL)
        surface.blit(lbl_lives, (x_lives, 4))

        icon_start_x = x_lives + 10
        icon_y = 26
        for i in range(max(0, lives)):
            self._draw_life_icon(
                surface=surface,
                is_invincible=invincible,
                x=icon_start_x + (i * 20),
                y=icon_y,
                radius=7,
            )

    def get_invincible_color(self) -> tuple[int, int, int]:
        """Generates a dynamic cycling RGB color using current
        ticks for invincibility feedback. Converts a hue angle derived
        from elapsed milliseconds into an RGB tuple.

        Returns:
            tuple[int, int, int]: An (R, G, B) tuple representing
            the active rainbow color.
        """
        current_time = pygame.time.get_ticks()
        hue = (current_time * 2) % 360
        color = pygame.Color(0, 0, 0)
        color.hsva = (hue, 100, 100, 100)
        return (color.r, color.g, color.b)
