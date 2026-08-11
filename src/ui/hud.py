import math
import pygame
import pygame.font


class HUD:
    """Gestiona la visualización del panel superior durante la partida."""

    def __init__(self, screen_width: int, screen_height: int):
        self.width = screen_width
        self.height = screen_height

        # Altura reservada para la barra del HUD
        self.hud_height = 45

        # Fuentes tipográficas
        self.font_label = pygame.font.SysFont("Arial", 12, bold=True)
        self.font_value = (
            pygame.font.SysFont("emulogic", 16)
            if "emulogic" in pygame.font.get_fonts()
            else pygame.font.SysFont("Arial", 18, bold=True)
        )

        # Paleta de colores Arcade
        self.COLOR_BG = (10, 10, 15)
        self.COLOR_BORDER = (33, 33, 222)        # Azul neón
        self.COLOR_LABEL = (180, 180, 190)       # Gris claro
        self.COLOR_SCORE = (255, 255, 255)       # Blanco
        self.COLOR_TIME_NORMAL = (0, 255, 255)   # Cian
        self.COLOR_TIME_WARN = (255, 50, 50)     # Rojo advertencia
        self.COLOR_LEVEL = (255, 183, 255)       # Rosa Pinky
        self.COLOR_PACMAN = (255, 255, 0)        # Amarillo Pac-Man

    def _draw_life_icon(self, surface: pygame.Surface, x: int, y: int, radius: int = 8) -> None:
        """Dibuja un icono procedural de Pac-Man con la boca abierta apuntando a la izquierda."""

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
        """Renderiza la barra superior del HUD con los 4 indicadores solicitados."""
        # Fondo y línea delimitadora azul neón
        hud_rect = pygame.Rect(0, 0, self.width, self.hud_height)
        pygame.draw.rect(surface, self.COLOR_BG, hud_rect)
        pygame.draw.line(surface, self.COLOR_BORDER, (0, self.hud_height), (self.width, self.hud_height), 2)

        padding_x = 30
        section_width = (self.width - (padding_x * 2)) // 4

        # ---------------------------------------------------------------------
        # 1. CURRENT SCORE
        # ---------------------------------------------------------------------
        x_score = padding_x
        lbl_score = self.font_label.render("SCORE", True, self.COLOR_LABEL)
        val_score = self.font_value.render(f"{score:05d}", True, self.COLOR_SCORE)

        surface.blit(lbl_score, (x_score, 4))
        surface.blit(val_score, (x_score, 18))

        # ---------------------------------------------------------------------
        # 2. REMAINING TIME
        # ---------------------------------------------------------------------
        x_time = padding_x + section_width
        time_color = self.COLOR_TIME_WARN if time_remaining <= 10 else self.COLOR_TIME_NORMAL

        lbl_time = self.font_label.render("TIME", True, self.COLOR_LABEL)
        val_time = self.font_value.render(f"{max(0, time_remaining):02d}s", True, time_color)

        surface.blit(lbl_time, (x_time, 4))
        surface.blit(val_time, (x_time, 18))

        # ---------------------------------------------------------------------
        # 3. CURRENT LEVEL
        # ---------------------------------------------------------------------
        x_level = padding_x + (section_width * 2)
        lbl_level = self.font_label.render("LEVEL", True, self.COLOR_LABEL)
        val_level = self.font_value.render(f"{level:02d}", True, self.COLOR_LEVEL)

        surface.blit(lbl_level, (x_level, 4))
        surface.blit(val_level, (x_level, 18))

        # ---------------------------------------------------------------------
        # 4. REMAINING LIVES
        # ---------------------------------------------------------------------
        x_lives = padding_x + (section_width * 3)
        lbl_lives = self.font_label.render("LIVES", True, self.COLOR_LABEL)
        surface.blit(lbl_lives, (x_lives, 4))

        # Dibujar tantos iconos de Pac-Man como vidas resten
        icon_start_x = x_lives + 10
        icon_y = 28
        for i in range(max(0, lives)):
            self._draw_life_icon(surface, icon_start_x + (i * 22), icon_y, radius=8)