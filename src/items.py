"""
items.py
--------
Collectible and interactive world objects: Time Crystals, Keys, and
locked Doors.
"""

import math
import pygame
import settings


class TimeCrystal:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.collected = False
        self.bob_offset = 0

    def update(self):
        self.bob_offset = math.sin(pygame.time.get_ticks() / 200) * 4

    def check_collected(self, player):
        if not self.collected and self.rect.colliderect(player.rect):
            self.collected = True
            return True
        return False

    def draw(self, surface, camera_x):
        if self.collected:
            return
        x = self.rect.centerx - camera_x
        y = self.rect.centery + self.bob_offset
        points = [(x, y - 10), (x + 8, y), (x, y + 10), (x - 8, y)]
        pygame.draw.polygon(surface, settings.LIGHT_VIOLET, points)
        pygame.draw.polygon(surface, settings.VIOLET, points, 2)


class Key:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 18, 18)
        self.collected = False

    def check_collected(self, player):
        if not self.collected and self.rect.colliderect(player.rect):
            self.collected = True
            player.has_key = True
            return True
        return False

    def draw(self, surface, camera_x):
        if self.collected:
            return
        x = self.rect.x - camera_x
        y = self.rect.y
        pygame.draw.circle(surface, settings.GOLD, (x + 5, y + 5), 5, 3)
        pygame.draw.rect(surface, settings.GOLD, (x + 8, y + 3, 10, 4))


class Door:
    """A locked door that disappears once the player has a key."""

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.unlocked = False

    def update(self, player):
        if player.has_key and not self.unlocked:
            if abs(player.rect.centerx - self.rect.centerx) < 60:
                self.unlocked = True
                player.has_key = False

    def draw(self, surface, camera_x):
        if self.unlocked:
            return
        x = self.rect.x - camera_x
        pygame.draw.rect(surface, settings.DARK_GOLD, (x, self.rect.y, self.rect.width, self.rect.height))
        pygame.draw.rect(surface, settings.DARK, (x, self.rect.y, self.rect.width, self.rect.height), 3)
        pygame.draw.circle(surface, settings.GOLD, (x + self.rect.width // 2, self.rect.y + self.rect.height // 2), 5)

    def blocks(self, player):
        return (not self.unlocked) and self.rect.colliderect(player.rect)


class EnergyPotion:
    """Blue flask. Restores Energy. If your energy is already full, it heals
    one life instead (up to the maximum)."""

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 26)
        self.collected = False
        self.bob_offset = 0

    def update(self):
        self.bob_offset = math.sin(pygame.time.get_ticks() / 250) * 3

    def check_collected(self, player):
        if not self.collected and self.rect.colliderect(player.rect):
            self.collected = True
            player.drink_potion()
            return True
        return False

    def draw(self, surface, camera_x):
        if self.collected:
            return
        x = self.rect.x - camera_x
        y = self.rect.y + self.bob_offset
        if x < -30 or x > settings.SCREEN_WIDTH + 30:
            return
        glow = pygame.Surface((44, 44), pygame.SRCALPHA)
        pygame.draw.circle(glow, (90, 170, 255, 70), (22, 22), 20)
        surface.blit(glow, (x - 12, y - 8))
        pygame.draw.rect(surface, (200, 200, 220), (x + 6, y, 8, 8))          # neck
        pygame.draw.rect(surface, settings.DARK_GOLD, (x + 5, y - 2, 10, 3))  # cork
        pygame.draw.ellipse(surface, (60, 140, 255), (x, y + 6, 20, 20))      # flask
        pygame.draw.ellipse(surface, (170, 220, 255), (x + 4, y + 10, 6, 6))  # shine
        pygame.draw.ellipse(surface, settings.WHITE, (x, y + 6, 20, 20), 2)
