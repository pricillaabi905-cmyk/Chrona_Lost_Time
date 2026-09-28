"""
rival.py
--------
Original rival princes Aria and Caleb encounter on their journey. Each
starts hostile (working for the true villain, the Hollow Sovereign) and
is defeated in a one-on-one duel - not killed, but bested - which plants
the seed of their eventual redemption. They reappear as allies in the
Level 5 climax.

These are original characters created for this game. Their names,
designs, and backstories are not based on any existing licensed IP.

- Idris the Shade: a shadow-magic mercenary, first duel in the Desert
  Kingdom (Level 3).
- Rowan of the Ice Court: a frost-magic guardian prince, first duel in
  the Frozen Kingdom (Level 4).

Gameplay: identical "stomp to duel" pattern as regular enemies, but
tougher (2 HP) and briefly invulnerable between hits so the fight has
some pacing.
"""

import pygame
import settings


class RivalPrince:
    def __init__(self, key, display_name, x, y, patrol_min, patrol_max,
                 color, accent_color, hp=2, speed=3):
        self.key = key                    # short id, used to look up dialogue
        self.display_name = display_name
        self.width = 34
        self.height = 54
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.patrol_min = patrol_min
        self.patrol_max = patrol_max
        self.color = color
        self.accent_color = accent_color
        self.speed = speed
        self.direction = 1

        self.max_hp = hp
        self.hp = hp
        self.alive = True
        self.defeated = False

        self.hit_flash = 0
        self.invuln_timer = 0
        self.vel_y = 0

    def update(self, platforms=None):
        if not self.alive:
            return
        if self.hit_flash > 0:
            self.hit_flash -= 1
        if self.invuln_timer > 0:
            self.invuln_timer -= 1

        self.rect.x += self.speed * self.direction
        if self.rect.left <= self.patrol_min:
            self.rect.left = self.patrol_min
            self.direction = 1
        elif self.rect.right >= self.patrol_max:
            self.rect.right = self.patrol_max
            self.direction = -1

        if platforms is not None:
            self.vel_y += settings.GRAVITY
            self.rect.y += self.vel_y
            for plat in platforms:
                if self.rect.colliderect(plat.rect) and self.vel_y > 0:
                    self.rect.bottom = plat.rect.top
                    self.vel_y = 0

    def check_player_collision(self, player):
        if not self.alive or player.invincible_timer > 0:
            return None
        if not self.rect.colliderect(player.rect):
            return None

        stomp = player.vel_y > 0 and player.rect.bottom - self.rect.top < 18
        if stomp and self.invuln_timer == 0:
            self.hp -= 1
            self.hit_flash = 10
            self.invuln_timer = 40
            player.vel_y = -9
            if self.hp <= 0:
                self.alive = False
                self.defeated = True
            return "hit_rival"
        else:
            direction = -1 if player.rect.centerx < self.rect.centerx else 1
            player.take_damage(1, knockback_dir=direction)
            return "hit_player"

    def draw(self, surface, camera_x):
        if not self.alive:
            return
        x = self.rect.x - camera_x
        y = self.rect.y

        body_color = settings.WHITE if self.hit_flash > 0 else self.color

        # cape
        pygame.draw.polygon(surface, self.accent_color, [
            (x + self.width // 2, y + 6), (x - 4, y + self.height), (x + self.width + 4, y + self.height)
        ])
        # legs
        pygame.draw.rect(surface, settings.DARK, (x + 6, y + 34, 8, 18))
        pygame.draw.rect(surface, settings.DARK, (x + self.width - 14, y + 34, 8, 18))
        # tunic
        pygame.draw.rect(surface, body_color, (x + 4, y + 16, self.width - 8, 22))
        pygame.draw.rect(surface, self.accent_color, (x + 4, y + 16, self.width - 8, 6))
        # head
        pygame.draw.circle(surface, (255, 224, 196), (x + self.width // 2, y + 10), 10)
        pygame.draw.ellipse(surface, settings.DARK, (x + 2, y - 2, self.width - 4, 16))

    def draw_hp_bar(self, surface):
        bar_width = 220
        bar_height = 14
        x = settings.SCREEN_WIDTH // 2 - bar_width // 2
        y = 20
        font = pygame.font.SysFont("georgia", 16, bold=True)
        label = font.render(self.display_name, True, settings.WHITE)
        surface.blit(label, label.get_rect(center=(settings.SCREEN_WIDTH // 2, y - 10)))
        pygame.draw.rect(surface, settings.DARK_GRAY, (x, y, bar_width, bar_height), border_radius=4)
        if self.hp > 0:
            fill_width = int(bar_width * (self.hp / self.max_hp))
            pygame.draw.rect(surface, self.accent_color, (x, y, fill_width, bar_height), border_radius=4)
        pygame.draw.rect(surface, settings.GOLD, (x, y, bar_width, bar_height), 2, border_radius=4)


def create_idris(x, y, patrol_min, patrol_max):
    """Idris the Shade - shadow-magic mercenary, first fought in the Desert Kingdom."""
    return RivalPrince(
        key="idris", display_name="Idris the Shade",
        x=x, y=y, patrol_min=patrol_min, patrol_max=patrol_max,
        color=(70, 60, 90), accent_color=(140, 60, 160), hp=2, speed=3,
    )


def create_rowan(x, y, patrol_min, patrol_max):
    """Rowan of the Ice Court - frost-magic guardian, first fought in the Frozen Kingdom."""
    return RivalPrince(
        key="rowan", display_name="Rowan of the Ice Court",
        x=x, y=y, patrol_min=patrol_min, patrol_max=patrol_max,
        color=(190, 220, 240), accent_color=(60, 120, 190), hp=2, speed=3,
    )
