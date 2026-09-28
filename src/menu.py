"""
menu.py
-------
Main menu (New Game / Continue Game / Level Map / Settings / Exit) and a
minimal Settings screen. Navigate with Up/Down, confirm with Enter/Space/E.
"""

import math
import pygame
import settings
from src.characters import draw_aria_figure, draw_caleb_figure


class MainMenu:
    def __init__(self, has_save):
        self.options = ["New Game", "Continue Game", "Level Map", "How to Play", "Settings", "Exit"]
        if not has_save:
            self.options.remove("Continue Game")
            self.options.remove("Level Map")
        self.selected = 0
        self.font_title = pygame.font.SysFont("georgia", 56, bold=True)
        self.font_option = pygame.font.SysFont("georgia", 28)
        self.font_sub = pygame.font.SysFont("georgia", 18)

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return None
        if event.key in settings.KEYS_UP:
            self.selected = (self.selected - 1) % len(self.options)
        elif event.key in settings.KEYS_DOWN:
            self.selected = (self.selected + 1) % len(self.options)
        elif event.key in (settings.KEY_INTERACT, settings.KEY_JUMP, pygame.K_RETURN, pygame.K_KP_ENTER):
            return self.options[self.selected]
        return None

    def draw(self, surface):
        surface.fill(settings.DARK)

        # decorative glowing crystal behind the title
        glow = 6 * math.sin(pygame.time.get_ticks() / 400)
        pygame.draw.circle(surface, settings.VIOLET,
                            (settings.SCREEN_WIDTH // 2, 130), int(40 + glow))
        pygame.draw.circle(surface, settings.LIGHT_VIOLET,
                            (settings.SCREEN_WIDTH // 2, 130), int(20 + glow))

        title = self.font_title.render(settings.GAME_TITLE, True, settings.GOLD)
        surface.blit(title, title.get_rect(center=(settings.SCREEN_WIDTH // 2, 230)))
        sub = self.font_sub.render("A Time-Travel Fantasy Adventure", True, settings.LIGHT_VIOLET)
        surface.blit(sub, sub.get_rect(center=(settings.SCREEN_WIDTH // 2, 275)))

        # Aria and Caleb flank the title, facing each other
        bob = 4 * math.sin(pygame.time.get_ticks() / 500)
        draw_aria_figure(surface, settings.SCREEN_WIDTH // 2 - 260, 195 + bob, scale=1.4)
        draw_caleb_figure(surface, settings.SCREEN_WIDTH // 2 + 190, 195 - bob, scale=1.4)

        start_y = 318
        for i, option in enumerate(self.options):
            color = settings.GOLD if i == self.selected else settings.WHITE
            text = f"> {option}" if i == self.selected else option
            opt_surf = self.font_option.render(text, True, color)
            surface.blit(opt_surf, opt_surf.get_rect(center=(settings.SCREEN_WIDTH // 2, start_y + i * 36)))


class SettingsMenu:
    """A minimal settings screen (placeholder for volume/controls display)."""

    def __init__(self):
        self.font_title = pygame.font.SysFont("georgia", 40, bold=True)
        self.font_option = pygame.font.SysFont("georgia", 22)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == settings.KEY_PAUSE:
            return "back"
        return None

    def draw(self, surface):
        surface.fill(settings.DARK)
        title = self.font_title.render("SETTINGS", True, settings.GOLD)
        surface.blit(title, title.get_rect(center=(settings.SCREEN_WIDTH // 2, 80)))

        lines = [
            "Controls (arrow keys AND WASD both work):",
            "  Move:           Left / Right   (A / D)",
            "  Jump:           Space or Up    (W)",
            "  Climb ladder:   Up / Down      (W / S)",
            "  Energy Bolt:    X",
            "  Enter portal:   Enter or E",
            "  Pause:          Escape",
            "  How to Play:    H (in game) or main menu",
            "",
            "Press Escape to return to the Main Menu",
        ]
        for i, line in enumerate(lines):
            color = settings.LIGHT_VIOLET if line.startswith("Controls") else settings.WHITE
            surf = self.font_option.render(line, True, color)
            surface.blit(surf, (settings.SCREEN_WIDTH // 2 - 300, 150 + i * 32))


class HowToPlay:
    """Two-page tutorial screen: Controls, then Enemies & Items.
    Left/Right (or A/D) flip pages. Enter/Space/E goes on. Esc closes."""

    ENEMIES = [
        ((200, 60, 60),   "Walker",     "Patrols back and forth. Jump on its head."),
        ((90, 60, 110),   "Bat",        "Flies in waves. Stomp it or shoot it."),
        ((80, 180, 90),   "Hopper",     "Frogs and frost slimes that hop. Time your jump."),
        ((190, 120, 50),  "Charger",    "Flashes red, then rushes you. Sidestep, then stomp."),
        ((60, 150, 70),   "Spitter",    "Rooted plant/turret that shoots. Jump its shots, or stomp it."),
        ((220, 220, 230), "Spiked",     "Spikes on top! NEVER stomp. Shoot it with X."),
        ((150, 140, 120), "Sentinel",   "Clockwork armour. Takes 2 stomps."),
        ((120, 80, 200),  "Wraith",     "Ghost that floats through walls. Only X hurts it (2 hits)."),
    ]

    def __init__(self):
        self.page = 0
        self.font_title = pygame.font.SysFont("georgia", 38, bold=True)
        self.font = pygame.font.SysFont("georgia", 20)
        self.font_key = pygame.font.SysFont("georgia", 20, bold=True)
        self.font_small = pygame.font.SysFont("georgia", 16)

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return None
        if event.key == settings.KEY_PAUSE:
            return "done"
        if event.key in settings.KEYS_LEFT:
            self.page = 0
        elif event.key in settings.KEYS_RIGHT:
            self.page = 1
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, settings.KEY_JUMP, settings.KEY_INTERACT):
            if self.page == 0:
                self.page = 1
            else:
                return "done"
        return None

    def _key_cap(self, surface, text, x, y):
        surf = self.font_key.render(text, True, settings.DARK)
        w = surf.get_width() + 16
        pygame.draw.rect(surface, settings.LIGHT_VIOLET, (x, y - 2, w, 28), border_radius=6)
        pygame.draw.rect(surface, settings.GOLD, (x, y - 2, w, 28), 2, border_radius=6)
        surface.blit(surf, (x + 8, y))
        return w

    def draw(self, surface):
        surface.fill(settings.DARK)
        W = settings.SCREEN_WIDTH
        title = self.font_title.render("HOW TO PLAY", True, settings.GOLD)
        surface.blit(title, title.get_rect(center=(W // 2, 42)))

        if self.page == 0:
            rows = [
                (["LEFT", "RIGHT"], "Walk   (or  A / D)"),
                (["SPACE"], "Jump  (jump over gaps and onto enemies)"),
                (["UP"], "Jump  (or  W)   -   climbs a ladder if you stand at one"),
                (["UP", "DOWN"], "Climb a ladder up / down   (or  W / S)"),
                (["X"], "Energy Bolt - costs 25 energy, hurts enemies from afar"),
                (["ENTER"], "Enter the glowing portal to finish the level  (or  E)"),
                (["ESC"], "Pause     |     H = open this help any time"),
            ]
            y = 88
            for keys, desc in rows:
                x = 60
                for k in keys:
                    x += self._key_cap(surface, k, x, y) + 8
                surface.blit(self.font.render(desc, True, settings.WHITE), (300, y))
                y += 37
            tips = [
                "GOAL: reach the portal at the end of each level. Collect Time Crystals on the way.",
                "Jump on enemies to defeat them.  Touching one from the side or spikes costs a heart.",
                "LADDER: stand in front of one and press UP or DOWN. Space jumps off.",
                "ENERGY POTION (blue flask): +50 energy. If your energy is full it heals 1 heart!",
                "Locked doors need the golden key.   Some levels also have a boss...",
            ]
            y += 4
            for t in tips:
                surface.blit(self.font_small.render(t, True, settings.LIGHT_VIOLET), (60, y))
                y += 22
        else:
            surface.blit(self.font.render("ENEMY GUIDE  -  every world has different monsters!",
                                          True, settings.LIGHT_VIOLET), (60, 82))
            y = 120
            for col, name, tip in self.ENEMIES:
                pygame.draw.circle(surface, col, (78, y + 11), 11)
                pygame.draw.circle(surface, settings.WHITE, (78, y + 11), 11, 2)
                surface.blit(self.font_key.render(name, True, settings.GOLD), (105, y))
                surface.blit(self.font_small.render(tip, True, settings.WHITE), (215, y + 3))
                y += 34
            # potion legend
            pygame.draw.ellipse(surface, (60, 140, 255), (66, y + 12, 24, 24))
            pygame.draw.ellipse(surface, settings.WHITE, (66, y + 12, 24, 24), 2)
            surface.blit(self.font_key.render("Energy Potion", True, settings.GOLD), (105, y + 12))
            surface.blit(self.font_small.render("Refills your energy bar (needed for X bolts).", True, settings.WHITE), (255, y + 15))

        foot = "<  >  change page      ENTER  continue      ESC  close"
        f = self.font_small.render(foot + f"      (page {self.page + 1}/2)", True, settings.GOLD)
        surface.blit(f, f.get_rect(center=(W // 2, settings.SCREEN_HEIGHT - 22)))


def draw_pause_overlay(surface, selected):
    overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((10, 5, 25, 190))
    surface.blit(overlay, (0, 0))

    font_title = pygame.font.SysFont("georgia", 46, bold=True)
    font_option = pygame.font.SysFont("georgia", 28)

    title = font_title.render("PAUSED", True, settings.GOLD)
    surface.blit(title, title.get_rect(center=(settings.SCREEN_WIDTH // 2, 180)))

    options = ["Resume", "How to Play", "Main Menu"]
    for i, option in enumerate(options):
        color = settings.GOLD if i == selected else settings.WHITE
        text = f"> {option}" if i == selected else option
        surf = font_option.render(text, True, color)
        surface.blit(surf, surf.get_rect(center=(settings.SCREEN_WIDTH // 2, 260 + i * 42)))
