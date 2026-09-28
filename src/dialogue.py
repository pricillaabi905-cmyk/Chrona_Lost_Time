"""
dialogue.py
-----------
A simple dialogue box system for story scenes before/after levels.
Each dialogue entry is a dict: {"name": "Aria", "text": "...", "color": (r,g,b)}
Press the Interact key (E), Space, or Enter to advance to the next line.
"""

import pygame
import settings


class DialogueBox:
    def __init__(self, lines, on_finish=None):
        """lines: list of dicts with 'name' and 'text' keys."""
        self.lines = lines
        self.index = 0
        self.on_finish = on_finish
        self.finished = False
        self.font_name = pygame.font.SysFont("georgia", 22)
        self.font_text = pygame.font.SysFont("georgia", 20)

    def advance(self):
        self.index += 1
        if self.index >= len(self.lines):
            self.finished = True
            if self.on_finish:
                self.on_finish()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (settings.KEY_INTERACT, settings.KEY_JUMP, pygame.K_RETURN):
                self.advance()

    def draw(self, surface):
        if self.finished or not self.lines:
            return
        line = self.lines[self.index]
        name = line.get("name", "")
        text = line.get("text", "")
        portrait_color = line.get("color", settings.VIOLET)

        box_h = 130
        box_rect = pygame.Rect(30, settings.SCREEN_HEIGHT - box_h - 20,
                                settings.SCREEN_WIDTH - 60, box_h)

        # semi-transparent background panel
        panel = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
        panel.fill((20, 15, 40, 220))
        surface.blit(panel, box_rect.topleft)
        pygame.draw.rect(surface, settings.GOLD, box_rect, 3, border_radius=8)

        # portrait - each named character gets its own original design
        portrait_center = (box_rect.left + 45, box_rect.top + 45)
        if name in (settings.BOSS_NAME, "???"):
            from src.boss import Villain
            Villain.draw_portrait(surface, portrait_center, radius=30)
        elif name == "Aria":
            from src.characters import draw_aria_portrait
            draw_aria_portrait(surface, portrait_center, radius=30)
        elif name == "Caleb":
            from src.characters import draw_caleb_portrait
            draw_caleb_portrait(surface, portrait_center, radius=30)
        elif name in ("Idris", "Idris the Shade", "Rowan", "Rowan of the Ice Court"):
            from src.asset_loader import draw_portrait_or_fallback
            key = "idris" if name.startswith("Idris") else "rowan"
            accent = (140, 60, 160) if key == "idris" else (60, 120, 190)
            base = (70, 60, 90) if key == "idris" else (190, 220, 240)

            def procedural(surface, center, radius, base=base, accent=accent):
                pygame.draw.circle(surface, base, center, radius)
                pygame.draw.circle(surface, accent, center, radius, 3)
                pygame.draw.circle(surface, (255, 224, 196), (center[0], center[1] - 4), 10)

            draw_portrait_or_fallback(surface, key, portrait_center, 30, procedural)
        else:
            pygame.draw.circle(surface, portrait_color, portrait_center, 30)
            pygame.draw.circle(surface, settings.GOLD, portrait_center, 30, 2)

        # name tag
        name_surf = self.font_name.render(name, True, settings.GOLD)
        surface.blit(name_surf, (box_rect.left + 90, box_rect.top + 14))

        # wrapped text
        wrapped = self._wrap_text(text, self.font_text, box_rect.width - 110)
        for i, line_text in enumerate(wrapped):
            text_surf = self.font_text.render(line_text, True, settings.WHITE)
            surface.blit(text_surf, (box_rect.left + 90, box_rect.top + 46 + i * 24))

        hint = self.font_text.render("Press E to continue...", True, settings.LIGHT_VIOLET)
        surface.blit(hint, (box_rect.right - hint.get_width() - 16, box_rect.bottom - 28))

    @staticmethod
    def _wrap_text(text, font, max_width):
        words = text.split(" ")
        lines = []
        current = ""
        for word in words:
            test = (current + " " + word).strip()
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines
