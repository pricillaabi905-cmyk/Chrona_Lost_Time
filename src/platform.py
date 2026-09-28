"""
platform.py
-----------
Simple solid platform / ground tile the player and enemies can stand on.
Supports an optional "ice" flag (Frozen Kingdom) which makes the surface
slippery, and a theme color so each world looks distinct.
"""

import pygame
import settings


class Platform:
    def __init__(self, x, y, width, height, color=settings.GRAY, is_ice=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.is_ice = is_ice

    def draw(self, surface, camera_x):
        draw_rect = pygame.Rect(self.rect.x - camera_x, self.rect.y, self.rect.width, self.rect.height)
        if draw_rect.right < 0 or draw_rect.left > settings.SCREEN_WIDTH:
            return  # off-screen, skip drawing for performance
        pygame.draw.rect(surface, self.color, draw_rect)
        edge_color = settings.ICE if self.is_ice else tuple(max(0, c - 30) for c in self.color)
        pygame.draw.rect(surface, edge_color, draw_rect, 3)


class Spike:
    """A static hazard (trap) that damages the player on contact."""

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface, camera_x):
        x = self.rect.x - camera_x
        y = self.rect.y
        w = self.rect.width
        h = self.rect.height
        spike_count = max(1, w // 12)
        spike_w = w / spike_count
        for i in range(spike_count):
            p1 = (x + i * spike_w, y + h)
            p2 = (x + i * spike_w + spike_w / 2, y)
            p3 = (x + (i + 1) * spike_w, y + h)
            pygame.draw.polygon(surface, settings.GRAY, [p1, p2, p3])
            pygame.draw.polygon(surface, settings.DARK_GRAY, [p1, p2, p3], 1)


class Ladder:
    """A climbable ladder. Stand in front of it and press UP / DOWN (or W / S).
    Its top edge lines up with the top of the platform it leads to."""

    WIDTH = 28

    def __init__(self, center_x, top_y, bottom_y):
        self.rect = pygame.Rect(center_x - self.WIDTH // 2, top_y, self.WIDTH, bottom_y - top_y)

    def draw(self, surface, camera_x):
        x = self.rect.x - camera_x
        if x + self.rect.width < 0 or x > settings.SCREEN_WIDTH:
            return
        top, bottom = self.rect.top, self.rect.bottom
        wood = (150, 105, 60)
        dark = (95, 65, 35)
        pygame.draw.rect(surface, wood, (x + 2, top, 5, self.rect.height))
        pygame.draw.rect(surface, wood, (x + self.rect.width - 7, top, 5, self.rect.height))
        pygame.draw.rect(surface, dark, (x + 2, top, 5, self.rect.height), 1)
        pygame.draw.rect(surface, dark, (x + self.rect.width - 7, top, 5, self.rect.height), 1)
        y = top + 10
        while y < bottom - 4:
            pygame.draw.rect(surface, wood, (x + 5, y, self.rect.width - 10, 5))
            pygame.draw.rect(surface, dark, (x + 5, y, self.rect.width - 10, 5), 1)
            y += 18
