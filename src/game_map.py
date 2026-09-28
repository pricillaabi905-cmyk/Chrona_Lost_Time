"""
game_map.py
-----------
The Level Map screen: shows all 5 levels as nodes on a path.
Each node is colored based on its state:
    - Completed  -> gold/filled
    - Current / unlocked -> violet, pulsing highlight
    - Locked -> gray, dimmed

Controls: Left/Right (or A/D) to move between nodes, Space/Enter/E to
select, Escape to go back to the main menu.
"""

import math
import pygame
import settings

LEVEL_NAMES = {
    1: "Ancient Temple",
    2: "Enchanted Forest",
    3: "Desert Kingdom",
    4: "Frozen Kingdom",
    5: "Royal Castle",
}


class LevelMap:
    def __init__(self, save_data):
        self.save_data = save_data
        self.selected = max(1, min(save_data.get("current_level", 1), settings.TOTAL_LEVELS))
        self.font_title = pygame.font.SysFont("georgia", 40, bold=True)
        self.font_label = pygame.font.SysFont("georgia", 18)
        self.font_hint = pygame.font.SysFont("georgia", 16)

    def node_state(self, level_num):
        if level_num in self.save_data.get("completed_levels", []):
            return "completed"
        if level_num <= self.save_data.get("highest_unlocked_level", 1):
            return "unlocked"
        return "locked"

    def handle_event(self, event):
        """Returns the chosen level number if the player confirms a selection,
        'back' if they want to return to the menu, otherwise None."""
        if event.type != pygame.KEYDOWN:
            return None
        if event.key in (pygame.K_LEFT, pygame.K_a):
            self.selected = max(1, self.selected - 1)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.selected = min(settings.TOTAL_LEVELS, self.selected + 1)
        elif event.key in (settings.KEY_INTERACT, settings.KEY_JUMP, pygame.K_RETURN):
            if self.node_state(self.selected) != "locked":
                return self.selected
        elif event.key == settings.KEY_PAUSE:
            return "back"
        return None

    def draw(self, surface):
        surface.fill(settings.DARK)

        title = self.font_title.render("LEVEL MAP", True, settings.GOLD)
        surface.blit(title, title.get_rect(center=(settings.SCREEN_WIDTH // 2, 60)))

        spacing = settings.SCREEN_WIDTH // (settings.TOTAL_LEVELS + 1)
        y = settings.SCREEN_HEIGHT // 2

        # path line
        pygame.draw.line(surface, settings.DARK_GRAY, (spacing, y), (spacing * settings.TOTAL_LEVELS, y), 4)

        for i in range(1, settings.TOTAL_LEVELS + 1):
            x = spacing * i
            state = self.node_state(i)

            if state == "completed":
                color = settings.GOLD
                radius = 26
            elif state == "unlocked":
                pulse = 4 * math.sin(pygame.time.get_ticks() / 250)
                color = settings.VIOLET
                radius = 30 + pulse
            else:
                color = settings.DARK_GRAY
                radius = 24

            pygame.draw.circle(surface, color, (x, y), int(radius))
            pygame.draw.circle(surface, settings.WHITE, (x, y), int(radius), 3)

            num_surf = self.font_title.render(str(i), True, settings.DARK)
            surface.blit(num_surf, num_surf.get_rect(center=(x, y)))

            # selection ring
            if i == self.selected:
                pygame.draw.circle(surface, settings.WHITE, (x, y), int(radius) + 8, 2)

            label = self.font_label.render(LEVEL_NAMES[i], True, settings.WHITE)
            surface.blit(label, label.get_rect(center=(x, y + 55)))

            state_label = {"completed": "Completed", "unlocked": "Unlocked", "locked": "Locked"}[state]
            state_color = settings.GOLD if state == "completed" else (
                settings.LIGHT_VIOLET if state == "unlocked" else settings.GRAY)
            state_surf = self.font_hint.render(state_label, True, state_color)
            surface.blit(state_surf, state_surf.get_rect(center=(x, y + 78)))

        hint = self.font_hint.render(
            "Left/Right: Move   E/Enter: Select   Esc: Back", True, settings.LIGHT_VIOLET)
        surface.blit(hint, hint.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT - 30)))

        crystals_surf = self.font_label.render(
            f"Time Crystals: {self.save_data.get('time_crystals', 0)}", True, settings.GOLD)
        surface.blit(crystals_surf, (20, 20))
