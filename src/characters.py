"""
characters.py
-------------
Reusable original character portrait art for the hero, Aria, and her ally,
Caleb - drawn procedurally with simple shapes (no external image files
needed). Used by the dialogue box and the main menu title screen.

These designs are wholly original to this project: Aria (violet/white/gold
time-traveler) and Caleb (blue/silver timeline wanderer). They are not
based on, and do not reproduce, any existing licensed character.
"""

import math
import pygame
import settings
from src.asset_loader import draw_portrait_or_fallback, get_sprite

CALEB_BLUE = (90, 140, 220)
CALEB_SILVER = (200, 210, 225)


def draw_aria_portrait(surface, center, radius=34):
    draw_portrait_or_fallback(surface, "aria", center, radius, _draw_aria_portrait_procedural)


def draw_caleb_portrait(surface, center, radius=34):
    draw_portrait_or_fallback(surface, "caleb", center, radius, _draw_caleb_portrait_procedural)


def _draw_aria_portrait_procedural(surface, center, radius=34):
    x, y = center
    pygame.draw.circle(surface, settings.WHITE, (x, y), radius)
    pygame.draw.circle(surface, settings.VIOLET, (x, y), radius, 2)
    # hair
    pygame.draw.ellipse(surface, settings.DARK, (x - radius + 4, y - radius, (radius - 4) * 2, radius + 6))
    # face
    pygame.draw.circle(surface, (255, 224, 196), (x, y + 2), radius - 14)
    # violet hood/collar accent
    pygame.draw.arc(surface, settings.VIOLET, (x - radius + 8, y + 6, (radius - 8) * 2, radius),
                     math.pi, 2 * math.pi, 4)
    # gold hourglass emblem
    pygame.draw.circle(surface, settings.GOLD, (x, y + radius - 10), 3)


def _draw_caleb_portrait_procedural(surface, center, radius=34):
    x, y = center
    pygame.draw.circle(surface, CALEB_SILVER, (x, y), radius)
    pygame.draw.circle(surface, CALEB_BLUE, (x, y), radius, 2)
    # short dark hair
    pygame.draw.ellipse(surface, settings.DARK, (x - radius + 6, y - radius, (radius - 6) * 2, radius))
    # face
    pygame.draw.circle(surface, (255, 224, 196), (x, y + 3), radius - 15)
    # high-collared blue cloak accent
    pygame.draw.arc(surface, CALEB_BLUE, (x - radius + 6, y + 4, (radius - 6) * 2, radius),
                     math.pi, 2 * math.pi, 4)
    # a faint clock/time motif on the collar to tie him to the timeline theme
    pygame.draw.circle(surface, CALEB_SILVER, (x, y + radius - 10), 4, 1)
    pygame.draw.line(surface, CALEB_SILVER, (x, y + radius - 10), (x, y + radius - 13), 1)


def draw_aria_figure(surface, x, y, scale=1.0):
    """A small full-body figure of Aria, used for menu/title decoration."""
    w, h = int(34 * scale), int(52 * scale)
    sprite = get_sprite("aria", target_size=(int(w * 1.3), int(h * 1.3)))
    if sprite:
        surface.blit(sprite, (x - w * 0.15, y - h * 0.1))
        return
    pygame.draw.polygon(surface, settings.VIOLET, [
        (x + w // 2, y + 6 * scale), (x - 4 * scale, y + h), (x + w + 4 * scale, y + h)
    ])
    pygame.draw.rect(surface, settings.DARK, (x + 6 * scale, y + 34 * scale, 8 * scale, 18 * scale))
    pygame.draw.rect(surface, settings.DARK, (x + w - 14 * scale, y + 34 * scale, 8 * scale, 18 * scale))
    pygame.draw.rect(surface, settings.WHITE, (x + 4 * scale, y + 16 * scale, w - 8 * scale, 22 * scale))
    pygame.draw.rect(surface, settings.VIOLET, (x + 4 * scale, y + 16 * scale, w - 8 * scale, 6 * scale))
    pygame.draw.circle(surface, (255, 224, 196), (int(x + w // 2), int(y + 10 * scale)), int(10 * scale))
    pygame.draw.ellipse(surface, settings.DARK, (x + 2 * scale, y - 2 * scale, w - 4 * scale, 18 * scale))


def draw_caleb_figure(surface, x, y, scale=1.0):
    """A small full-body figure of Caleb, used for menu/title decoration."""
    w, h = int(34 * scale), int(54 * scale)
    sprite = get_sprite("caleb", target_size=(int(w * 1.3), int(h * 1.3)))
    if sprite:
        surface.blit(sprite, (x - w * 0.15, y - h * 0.1))
        return
    pygame.draw.polygon(surface, CALEB_BLUE, [
        (x + w // 2, y + 6 * scale), (x - 4 * scale, y + h), (x + w + 4 * scale, y + h)
    ])
    pygame.draw.rect(surface, settings.DARK, (x + 6 * scale, y + 36 * scale, 8 * scale, 18 * scale))
    pygame.draw.rect(surface, settings.DARK, (x + w - 14 * scale, y + 36 * scale, 8 * scale, 18 * scale))
    pygame.draw.rect(surface, CALEB_SILVER, (x + 4 * scale, y + 16 * scale, w - 8 * scale, 24 * scale))
    pygame.draw.rect(surface, CALEB_BLUE, (x + 4 * scale, y + 16 * scale, w - 8 * scale, 6 * scale))
    pygame.draw.circle(surface, (255, 224, 196), (int(x + w // 2), int(y + 10 * scale)), int(10 * scale))
    pygame.draw.ellipse(surface, settings.DARK, (x + 3 * scale, y - 1 * scale, w - 6 * scale, 14 * scale))
