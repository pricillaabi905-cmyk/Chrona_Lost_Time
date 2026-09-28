"""
portal.py
---------
The magical portal that ends a level and transports Aria to the next
timeline. The player must walk into it and press the Interact key (E).
"""

import math
import pygame
import settings


class Portal:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 44, 70)
        self.active = True

    def player_in_range(self, player):
        return self.active and self.rect.colliderect(player.rect.inflate(20, 20))

    def draw(self, surface, camera_x):
        x = self.rect.centerx - camera_x
        y = self.rect.centery
        t = pygame.time.get_ticks() / 150
        for i in range(6):
            radius = 10 + i * 5 + math.sin(t + i) * 3
            color_shift = min(255, 120 + i * 20)
            color = (color_shift, 90, 230 - i * 10)
            pygame.draw.ellipse(
                surface, color,
                (x - radius // 2, y - self.rect.height // 2, radius, self.rect.height)
            )
        pygame.draw.ellipse(surface, settings.WHITE,
                             (x - 6, y - self.rect.height // 2 + 6, 12, self.rect.height - 12), 0)
