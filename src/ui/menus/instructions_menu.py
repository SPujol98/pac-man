import pygame
from typing import Optional, List, Tuple
from states import GameState


class InstructionsMenu:
    """Navigate the instruction screen using visual cards, stylized buttons, and a retro look."""

    def __init__(self, screen_width: int, screen_height: int):
        self.width = screen_width
        self.height = screen_height

        self.title_font = (
            pygame.font.SysFont("emulogic", 28)
            if "emulogic" in pygame.font.get_fonts()
            else pygame.font.SysFont("Arial", 32, bold=True)
        )
        self.section_font = pygame.font.SysFont("Arial", 18, bold=True)
        self.label_font = pygame.font.SysFont("Arial", 15, bold=True)
        self.body_font = pygame.font.SysFont("Arial", 14)
        self.key_font = pygame.font.SysFont("Arial", 12, bold=True)

        self.COLOR_BG = (10, 10, 15)
        self.COLOR_TITLE = (255, 255, 0)
        self.COLOR_BORDER = (33, 33, 222)
        self.COLOR_HEADER = (255, 183, 255)
        self.COLOR_TEXT = (220, 220, 220)
        self.COLOR_KEY_BG = (40, 40, 50)
        self.COLOR_KEY_BORDER = (0, 255, 255)
        self.COLOR_DOT = (255, 183, 82)

    def handle_event(self, event: pygame.event.Event) -> Optional[GameState]:
        """Press the ESC key to return to the main menu."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return GameState.MENU
        return GameState.INSTRUCTIONS

    def _draw_key_badge(self, surface: pygame.Surface, text: str, x: int, y: int) -> int:
        """Draw a stylized key that looks like an arcade button and return its width."""
        text_surf = self.key_font.render(text, True, (255, 255, 255))
        padding_x, padding_y = 8, 4
        width = text_surf.get_width() + (padding_x * 2)
        height = text_surf.get_height() + (padding_y * 2)

        rect = pygame.Rect(x, y, width, height)

        pygame.draw.rect(surface, (0, 0, 0), rect.move(2, 2), border_radius=4)
        pygame.draw.rect(surface, self.COLOR_KEY_BG, rect, border_radius=4)
        pygame.draw.rect(surface, self.COLOR_KEY_BORDER, rect, width=1, border_radius=4)

        surface.blit(text_surf, (x + padding_x, y + padding_y))
        return width

    def _draw_card(self, surface: pygame.Surface, rect: pygame.Rect, title: str) -> None:
        """Draw a card or panel with the title incorporated into the border."""

        pygame.draw.rect(surface, (15, 15, 25), rect, border_radius=8)
        pygame.draw.rect(surface, self.COLOR_BORDER, rect, width=2, border_radius=8)

        title_surf = self.section_font.render(f"  {title}  ", True, self.COLOR_HEADER)
        title_rect = title_surf.get_rect(midtop=(rect.centerx, rect.top - 10))
        
        bg_patch = pygame.Rect(title_rect.x, rect.top - 2, title_rect.width, 4)
        pygame.draw.rect(surface, (15, 15, 25), bg_patch)
        surface.blit(title_surf, title_rect)

    def draw(self, surface: pygame.Surface) -> None:
        """Renderiza la pantalla completa con tarjetas ordenadas y elementos gráficos."""
        surface.fill(self.COLOR_BG)
        title_surf = self.title_font.render("HOW TO PLAY", True, self.COLOR_TITLE)
        title_rect = title_surf.get_rect(center=(self.width // 2, 40))
        surface.blit(title_surf, title_rect)

        line_y = 40
        margin_lines = 40
        pygame.draw.line(surface, self.COLOR_BORDER, (margin_lines, line_y), (title_rect.left - 20, line_y), 3)
        pygame.draw.line(surface, self.COLOR_BORDER, (title_rect.right + 20, line_y), (self.width - margin_lines, line_y), 3)

        controls_rect = pygame.Rect(40, 80, self.width - 80, 110)
        self._draw_card(surface, controls_rect, "CONTROLS")

        lbl_move = self.label_font.render("MOVE:", True, (255, 255, 255))
        surface.blit(lbl_move, (60, 110))
        
        curr_x = 130
        curr_x += self._draw_key_badge(surface, "W A S D", curr_x, 107) + 10
        curr_x += self._draw_key_badge(surface, "ARROWS", curr_x, 107) + 15
        
        desc_move = self.body_font.render("Navigate Pac-Man through the maze corridors.", True, self.COLOR_TEXT)
        surface.blit(desc_move, (curr_x, 110))

        lbl_pause = self.label_font.render("PAUSE:", True, (255, 255, 255))
        surface.blit(lbl_pause, (60, 148))
        
        curr_x = 130
        curr_x += self._draw_key_badge(surface, "P", curr_x, 145) + 15
        
        desc_pause = self.body_font.render("Pause or resume the game at any time.", True, self.COLOR_TEXT)
        surface.blit(desc_pause, (curr_x, 148))

        rules_rect = pygame.Rect(40, 215, self.width - 80, 310)
        self._draw_card(surface, rules_rect, "RULES & OBJECTIVES")

        rules: List[Tuple[str, str]] = [
            ("COLLECT", "Eat pacgums for points. Super-pacgums turn ghosts blue so you can eat them."),
            ("SURVIVE", "Avoid ghosts! You have 3 lives. Catching a ghost resets your position."),
            ("WIN LEVEL", "Eat all pacgums in the maze before time runs out to advance."),
            ("GAME OVER", "Losing all lives ends the game. You can record your high score!"),
        ]

        start_y = 245
        for label, text in rules:
            pygame.draw.circle(surface, self.COLOR_DOT, (65, start_y + 8), 4)
            lbl_surf = self.label_font.render(f"{label}:", True, self.COLOR_HEADER)
            surface.blit(lbl_surf, (80, start_y))
            desc_surf = self.body_font.render(text, True, self.COLOR_TEXT)
            surface.blit(desc_surf, (190, start_y))

            start_y += 38

        goal_box = pygame.Rect(60, start_y + 10, rules_rect.width - 40, 40)
        pygame.draw.rect(surface, (25, 25, 45), goal_box, border_radius=6)
        pygame.draw.rect(surface, (0, 255, 255), goal_box, width=1, border_radius=6)

        goal_text = "GOAL: Clear every level and achieve the highest score!"
        goal_surf = self.section_font.render(goal_text, True, (0, 255, 255))
        goal_rect = goal_surf.get_rect(center=goal_box.center)
        surface.blit(goal_surf, goal_rect)

        esc_x = (self.width // 2) - 120
        badge_w = self._draw_key_badge(surface, "ESC", esc_x, self.height - 35)
        
        footer_surf = self.body_font.render("Return to Main Menu", True, (150, 150, 150))
        surface.blit(footer_surf, (esc_x + badge_w + 10, self.height - 33))