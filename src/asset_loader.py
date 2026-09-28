"""
asset_loader.py
----------------
Safely loads character images from assets/images/characters/ if they
exist, so you can drop in real artwork later without touching any game
code. If an image is missing, everything falls back to the existing
procedurally-drawn art automatically - the game never crashes because
an image file isn't there yet.

Expected file naming (all optional - add whichever you have):

    assets/images/characters/<name>_sprite.png    - in-level sprite
    assets/images/characters/<name>_portrait.png  - dialogue/menu portrait

Where <name> is one of: aria, caleb, idris, rowan, hollow_sovereign,
timewyrm

Recommended format: PNG with a transparent background.
Recommended sizes:
    sprite:   roughly 128x196 px (will be scaled down to fit the
              character's in-game hitbox, so any size works, but a
              tall portrait-style crop reads best)
    portrait: roughly 256x256 px, square, face/bust framed in the
              center (it gets cropped to a circle automatically)
"""

import os
import pygame
import settings

CHARACTERS_DIR = os.path.join(settings.BASE_DIR, "assets", "images", "characters")

_cache = {}


def _load_raw(filename):
    if filename in _cache:
        return _cache[filename]
    path = os.path.join(CHARACTERS_DIR, filename)
    image = None
    if os.path.isfile(path):
        try:
            image = pygame.image.load(path).convert_alpha()
        except (pygame.error, OSError):
            image = None
    _cache[filename] = image
    return image


def get_sprite(name, target_size=None):
    """Returns a pygame Surface for <name>_sprite.png, scaled to
    target_size=(w, h) if given, or None if the file doesn't exist yet."""
    image = _load_raw(f"{name}_sprite.png")
    if image is None:
        return None
    if target_size:
        image = pygame.transform.smoothscale(image, target_size)
    return image


def get_portrait(name, diameter=60):
    """Returns a circular-cropped pygame Surface for <name>_portrait.png
    sized to fit a (diameter x diameter) circle, or None if missing."""
    image = _load_raw(f"{name}_portrait.png")
    if image is None:
        return None

    # scale to cover a (diameter x diameter) square, then crop to a circle
    size = max(diameter, 1)
    w, h = image.get_size()
    scale = size / min(w, h)
    scaled = pygame.transform.smoothscale(image, (int(w * scale), int(h * scale)))

    sx, sy = scaled.get_size()
    crop_rect = pygame.Rect((sx - size) // 2, (sy - size) // 2, size, size)
    square = scaled.subsurface(crop_rect).copy()

    mask = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (size // 2, size // 2), size // 2)
    square.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return square


def draw_portrait_or_fallback(surface, name, center, radius, fallback_draw_fn):
    """Draws the real portrait image if it exists; otherwise calls
    fallback_draw_fn(surface, center, radius) to use the procedural art."""
    portrait = get_portrait(name, diameter=radius * 2)
    if portrait:
        surface.blit(portrait, (center[0] - radius, center[1] - radius))
        pygame.draw.circle(surface, settings.GOLD, center, radius, 2)
    else:
        fallback_draw_fn(surface, center, radius)
