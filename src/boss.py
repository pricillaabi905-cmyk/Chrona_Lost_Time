"""
boss.py
-------
The main villain and the climactic monster fight for the end of Level 5.

Story role: "The Hollow Sovereign" is the true villain behind the broken
timeline - he usurped Caleb's throne the moment Caleb walked away from
it, and has been draining the World Dragon's crystal heart (the source
of every "Time Crystal" Aria collects) to fuel his own power. He
summons "The Timewyrm" to stop Aria and Caleb before they can reach him
and save the dragon.

(Rival-prince duels - Idris in the Desert Kingdom, Rowan in the Frozen
Kingdom - live in src/rival.py, not here; this file is only the final
villain + monster.)

These are original characters created for this game - their names,
designs, and backstories are not based on any existing licensed IP.

Gameplay: The Timewyrm has 3 hit points. It patrols and periodically
telegraphs a lunge attack (flashes red) before charging at the player.
Aria defeats it by jumping on top of it, same as other enemies - it
just takes three successful stomps, and touching it from the side
(especially during a lunge) costs a life.
"""

import pygame
import settings


class Villain:
    """The Hollow Sovereign - a dialogue/cutscene-only character. He
    never fights directly; he sends the Timewyrm (and, earlier, Idris
    and Rowan) to stop Aria and Caleb for him."""

    name = settings.BOSS_NAME
    portrait_color = settings.VILLAIN_VIOLET

    @staticmethod
    def draw_portrait(surface, center, radius=30):
        from src.asset_loader import draw_portrait_or_fallback
        draw_portrait_or_fallback(surface, "hollow_sovereign", center, radius, Villain._draw_portrait_procedural)

    @staticmethod
    def _draw_portrait_procedural(surface, center, radius=30):
        x, y = center
        pygame.draw.circle(surface, settings.VILLAIN_VIOLET, (x, y), radius)
        pygame.draw.circle(surface, settings.DARK, (x, y), radius, 2)
        hood_points = [(x - radius, y), (x, y - radius - 8), (x + radius, y)]
        pygame.draw.polygon(surface, settings.DARK, hood_points)
        pygame.draw.circle(surface, settings.VILLAIN_RED, (x - 8, y - 2), 3)
        pygame.draw.circle(surface, settings.VILLAIN_RED, (x + 8, y - 2), 3)
        # cracked-crown motif - he wears a stolen crown
        for dx in (-14, -5, 5, 14):
            pygame.draw.line(surface, settings.DARK_GOLD,
                              (x + dx, y - radius - 6), (x + dx, y - radius + 2), 2)


class TimewyrmBoss:
    """The monster boss fight itself - a serpentine, dragon-winged
    time-corrupted beast summoned by the Hollow Sovereign."""

    def __init__(self, x, y, patrol_min, patrol_max):
        self.width = 70
        self.height = 60
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.patrol_min = patrol_min
        self.patrol_max = patrol_max
        self.speed = 2
        self.direction = 1

        self.max_hp = settings.BOSS_MAX_HP
        self.hp = self.max_hp
        self.alive = True
        self.defeated = False

        self.state = "patrol"  # patrol -> telegraph -> lunge -> cooldown
        self.state_timer = 0
        self.telegraph_time = 45
        self.lunge_time = 30
        self.cooldown_time = 60
        self.lunge_speed = 9

        self.hit_flash = 0
        self.invuln_timer = 0

    def update(self, player):
        if not self.alive:
            return

        if self.hit_flash > 0:
            self.hit_flash -= 1
        if self.invuln_timer > 0:
            self.invuln_timer -= 1

        if self.state == "patrol":
            self.rect.x += self.speed * self.direction
            if self.rect.left <= self.patrol_min:
                self.direction = 1
            elif self.rect.right >= self.patrol_max:
                self.direction = -1
            self.state_timer += 1
            if self.state_timer > 90:
                self.state = "telegraph"
                self.state_timer = 0
                self.direction = 1 if player.rect.centerx > self.rect.centerx else -1

        elif self.state == "telegraph":
            self.state_timer += 1
            if self.state_timer >= self.telegraph_time:
                self.state = "lunge"
                self.state_timer = 0

        elif self.state == "lunge":
            self.rect.x += self.lunge_speed * self.direction
            self.rect.x = max(self.patrol_min, min(self.rect.x, self.patrol_max - self.width))
            self.state_timer += 1
            if self.state_timer >= self.lunge_time:
                self.state = "cooldown"
                self.state_timer = 0

        elif self.state == "cooldown":
            self.state_timer += 1
            if self.state_timer >= self.cooldown_time:
                self.state = "patrol"
                self.state_timer = 0

    def check_player_collision(self, player):
        if not self.alive or player.invincible_timer > 0:
            return None
        if not self.rect.colliderect(player.rect):
            return None

        stomp = player.vel_y > 0 and player.rect.bottom - self.rect.top < 20
        if stomp and self.invuln_timer == 0:
            self.hp -= 1
            self.hit_flash = 12
            self.invuln_timer = 45
            player.vel_y = -10
            if self.hp <= 0:
                self.alive = False
                self.defeated = True
            return "hit_boss"
        else:
            direction = -1 if player.rect.centerx < self.rect.centerx else 1
            dmg = 2 if self.state == "lunge" else 1
            player.take_damage(dmg, knockback_dir=direction)
            return "hit_player"

    def draw(self, surface, camera_x):
        if not self.alive:
            return
        x = self.rect.x - camera_x
        y = self.rect.y

        base_color = settings.MONSTER_COLOR
        if self.hit_flash > 0:
            body_color = settings.WHITE
        elif self.state == "telegraph":
            pulse = 255 if (self.state_timer // 6) % 2 == 0 else 120
            body_color = (pulse, 30, 30)
        else:
            body_color = base_color

        for i in range(3):
            seg_x = x + i * 18 if self.direction > 0 else x + self.width - 18 - i * 18
            pygame.draw.ellipse(surface, body_color, (seg_x, y + 10 + i * 4, 34, 34))

        head_x = x + self.width - 24 if self.direction > 0 else x
        pygame.draw.ellipse(surface, body_color, (head_x, y, 44, 40))

        # small wings - reads clearly as a dragon, not just a serpent
        wing_y = y + 4
        pygame.draw.polygon(surface, settings.DARK_GOLD, [
            (x + self.width // 2 - 12, wing_y), (x + self.width // 2, wing_y - 18),
            (x + self.width // 2 + 12, wing_y)
        ])

        eye_x = head_x + 30 if self.direction > 0 else head_x + 14
        pygame.draw.circle(surface, settings.VILLAIN_RED, (eye_x, y + 14), 5)
        pygame.draw.circle(surface, settings.WHITE, (eye_x, y + 14), 2)

        for i in range(4):
            sx = x + 10 + i * 14
            pygame.draw.polygon(surface, settings.DARK_GOLD,
                                 [(sx, y + 8), (sx + 5, y - 4), (sx + 10, y + 8)])

    def draw_hp_bar(self, surface):
        bar_width = 300
        bar_height = 18
        x = settings.SCREEN_WIDTH // 2 - bar_width // 2
        y = 20

        font = pygame.font.SysFont("georgia", 18, bold=True)
        label = font.render(settings.BOSS_MONSTER_NAME, True, settings.WHITE)
        surface.blit(label, label.get_rect(center=(settings.SCREEN_WIDTH // 2, y - 10)))

        pygame.draw.rect(surface, settings.DARK_GRAY, (x, y, bar_width, bar_height), border_radius=4)
        if self.hp > 0:
            fill_width = int(bar_width * (self.hp / self.max_hp))
            pygame.draw.rect(surface, settings.VILLAIN_RED, (x, y, fill_width, bar_height), border_radius=4)
        pygame.draw.rect(surface, settings.GOLD, (x, y, bar_width, bar_height), 2, border_radius=4)
