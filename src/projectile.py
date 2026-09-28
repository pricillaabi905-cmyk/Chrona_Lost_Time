"""
projectile.py
-------------
Moving shots: enemy projectiles (thorns, ice shards, sand bolts...) that hurt
the player, and the player's Energy Bolt (fired with X) that hurts enemies.
"""

import pygame


class Projectile:
    def __init__(self, x, y, vx, vy=0, color=(255, 120, 80), radius=6,
                 from_player=False, life=150):
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.color = color
        self.radius = radius
        self.from_player = from_player
        self.life = life
        self.alive = True
        self.rect = pygame.Rect(0, 0, radius * 2, radius * 2)
        self.rect.center = (int(x), int(y))

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (int(self.x), int(self.y))
        self.life -= 1
        if self.life <= 0:
            self.alive = False

    def draw(self, surface, camera_x):
        cx = int(self.x) - camera_x
        cy = int(self.y)
        if cx < -20 or cx > 980:
            return
        if self.from_player:
            pygame.draw.circle(surface, (120, 200, 255), (cx, cy), self.radius + 4)
            pygame.draw.circle(surface, (255, 255, 255), (cx, cy), self.radius)
        else:
            pygame.draw.circle(surface, (40, 20, 30), (cx, cy), self.radius + 2)
            pygame.draw.circle(surface, self.color, (cx, cy), self.radius)
