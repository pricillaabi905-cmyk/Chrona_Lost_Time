"""
enemy.py
--------
All regular (non-boss) enemies. Every enemy type behaves differently, so each
world feels fresh:

    Enemy (walker)   - patrols back and forth. Stomp it.
    BatEnemy         - flies in a wave. Stomp it or shoot it.
    HopperEnemy      - hops as it patrols (frogs, frost slimes). Stomp it.
    ChargerEnemy     - flashes red, then rushes you. Stomp it.
    SpitterEnemy     - stands still and shoots projectiles. Stomp it.
    SpikedEnemy      - spiked shell: NEVER stomp! Shoot it with an Energy Bolt.
    SentinelEnemy    - clockwork armour: needs 2 stomps.
    WraithEnemy      - ghost that drifts through walls to chase you.
                       Stomping does nothing; needs 2 Energy Bolts.

Shared interface (used by Level):
    update(platforms, player)   check_player_collision(player)
    take_bolt() -> bool         spawn_queue (list of new Projectiles)
"""

import math
import pygame
import settings
from src.projectile import Projectile


class Enemy:
    """Basic walker. Also the base class for every other enemy."""
    stompable = True
    label = "Walker"

    def __init__(self, x, y, width, height, x_min, x_max, speed=2, color=settings.RED):
        self.rect = pygame.Rect(x, y, width, height)
        self.x_min = x_min
        self.x_max = x_max
        self.speed = speed
        self.direction = 1
        self.color = color
        self.alive = True
        self.vel_y = 0
        self.hp = 1
        self.flash = 0
        self.invuln = 0
        self.t = 0
        self.spawn_queue = []

    # -- helpers -------------------------------------------------------
    def _tick(self):
        self.t += 1
        if self.flash > 0:
            self.flash -= 1
        if self.invuln > 0:
            self.invuln -= 1

    def _patrol(self):
        self.rect.x += self.speed * self.direction
        if self.rect.left <= self.x_min:
            self.rect.left = self.x_min
            self.direction = 1
        elif self.rect.right >= self.x_max:
            self.rect.right = self.x_max
            self.direction = -1

    def _gravity(self, platforms):
        self.vel_y = min(self.vel_y + settings.GRAVITY, settings.MAX_FALL_SPEED)
        self.rect.y += int(round(self.vel_y))
        landed = False
        if platforms:
            for plat in platforms:
                if self.rect.colliderect(plat.rect) and self.vel_y > 0:
                    self.rect.bottom = plat.rect.top
                    self.vel_y = 0
                    landed = True
        return landed

    def _color(self):
        return settings.WHITE if self.flash > 0 else self.color

    # -- behaviour -----------------------------------------------------
    def update(self, platforms=None, player=None):
        if not self.alive:
            return
        self._tick()
        self._patrol()
        self._gravity(platforms)

    def take_bolt(self):
        """Hit by the player's Energy Bolt. Returns True if it hit."""
        if not self.alive:
            return False
        self.hp -= 1
        self.flash = 8
        if self.hp <= 0:
            self.alive = False
        return True

    def check_player_collision(self, player):
        """Returns 'defeated', 'bounced', 'hit', or None."""
        if not self.alive or player.invincible_timer > 0:
            return None
        if not self.rect.colliderect(player.rect):
            return None
        if self.invuln > 0:
            return None

        stomped = player.vel_y > 0 and player.rect.bottom - self.rect.top < 18
        if stomped and self.stompable:
            self.hp -= 1
            self.flash = 8
            player.vel_y = -9
            if self.hp <= 0:
                self.alive = False
                return "defeated"
            self.invuln = 30
            return "bounced"

        direction = -1 if player.rect.centerx < self.rect.centerx else 1
        player.take_damage(1, knockback_dir=direction)
        return "hit"

    # -- drawing -------------------------------------------------------
    def _screen_pos(self, camera_x):
        x = self.rect.x - camera_x
        if x + self.rect.width < 0 or x > settings.SCREEN_WIDTH:
            return None
        return x, self.rect.y

    def _eyes(self, surface, x, y, w, h, angry=False):
        ey = y + h // 3
        for ex in (x + w // 3, x + 2 * w // 3):
            pygame.draw.circle(surface, settings.WHITE, (ex, ey), 3)
            pygame.draw.circle(surface, settings.BLACK, (ex + self.direction, ey), 1)
        if angry:
            pygame.draw.line(surface, settings.BLACK, (x + w // 3 - 4, ey - 5), (x + w // 3 + 3, ey - 2), 2)
            pygame.draw.line(surface, settings.BLACK, (x + 2 * w // 3 + 4, ey - 5), (x + 2 * w // 3 - 3, ey - 2), 2)

    def draw(self, surface, camera_x):
        if not self.alive:
            return
        pos = self._screen_pos(camera_x)
        if not pos:
            return
        x, y = pos
        w, h = self.rect.size
        pygame.draw.ellipse(surface, self._color(), (x, y, w, h))
        self._eyes(surface, x, y, w, h)


# ---------------------------------------------------------------------------
class BatEnemy(Enemy):
    """Flies left/right in a smooth wave. Ignores gravity."""
    label = "Bat"

    def __init__(self, x, base_y, x_min, x_max, speed=2, amp=40, color=(90, 60, 110)):
        super().__init__(x, base_y, 34, 22, x_min, x_max, speed, color)
        self.base_y = base_y
        self.amp = amp

    def update(self, platforms=None, player=None):
        if not self.alive:
            return
        self._tick()
        self._patrol()
        self.rect.y = int(self.base_y + math.sin(self.t / 25) * self.amp)

    def draw(self, surface, camera_x):
        if not self.alive:
            return
        pos = self._screen_pos(camera_x)
        if not pos:
            return
        x, y = pos
        flap = math.sin(self.t / 4) * 9
        c = self._color()
        cx = x + 17
        pygame.draw.polygon(surface, c, [(cx - 4, y + 10), (cx - 24, y + 2 - flap), (cx - 16, y + 18)])
        pygame.draw.polygon(surface, c, [(cx + 4, y + 10), (cx + 24, y + 2 - flap), (cx + 16, y + 18)])
        pygame.draw.ellipse(surface, c, (x + 7, y + 4, 20, 18))
        pygame.draw.circle(surface, (255, 220, 80), (cx - 4, y + 11), 2)
        pygame.draw.circle(surface, (255, 220, 80), (cx + 4, y + 11), 2)


# ---------------------------------------------------------------------------
class HopperEnemy(Enemy):
    """Patrols while hopping (forest frogs, frost slimes)."""
    label = "Hopper"

    def __init__(self, x, y, x_min, x_max, speed=2, color=(80, 180, 90), hop=-11):
        super().__init__(x, y, 32, 30, x_min, x_max, speed, color)
        self.hop = hop
        self.on_ground = False
        self.timer = 40

    def update(self, platforms=None, player=None):
        if not self.alive:
            return
        self._tick()
        if self.on_ground:
            self.timer -= 1
            if self.timer <= 0:
                self.vel_y = self.hop
                self.on_ground = False
                self.timer = 50
        else:
            self._patrol()
        self.on_ground = self._gravity(platforms)

    def draw(self, surface, camera_x):
        if not self.alive:
            return
        pos = self._screen_pos(camera_x)
        if not pos:
            return
        x, y = pos
        squash = 4 if self.on_ground else 0
        pygame.draw.ellipse(surface, self._color(), (x - squash, y + squash, 32 + 2 * squash, 30 - squash))
        pygame.draw.circle(surface, settings.WHITE, (x + 9, y + 8), 5)
        pygame.draw.circle(surface, settings.WHITE, (x + 23, y + 8), 5)
        pygame.draw.circle(surface, settings.BLACK, (x + 9 + self.direction * 2, y + 8), 2)
        pygame.draw.circle(surface, settings.BLACK, (x + 23 + self.direction * 2, y + 8), 2)


# ---------------------------------------------------------------------------
class ChargerEnemy(Enemy):
    """Walks slowly; when it sees you it flashes red, then charges."""
    label = "Charger"

    def __init__(self, x, y, x_min, x_max, color=(190, 120, 50), sight=260):
        super().__init__(x, y, 36, 36, x_min, x_max, 1, color)
        self.state = "patrol"
        self.timer = 0
        self.sight = sight

    def update(self, platforms=None, player=None):
        if not self.alive:
            return
        self._tick()
        if self.state == "patrol":
            self.speed = 1
            self._patrol()
            if player and abs(player.rect.centerx - self.rect.centerx) < self.sight \
                    and abs(player.rect.bottom - self.rect.bottom) < 60 \
                    and self.x_min <= player.rect.centerx <= self.x_max:
                self.state, self.timer = "warn", 28
                self.direction = 1 if player.rect.centerx > self.rect.centerx else -1
        elif self.state == "warn":
            self.timer -= 1
            if self.timer <= 0:
                self.state, self.timer = "charge", 45
        elif self.state == "charge":
            self.speed = 6
            self._patrol()
            self.timer -= 1
            if self.timer <= 0:
                self.state, self.timer = "rest", 60
        elif self.state == "rest":
            self.timer -= 1
            if self.timer <= 0:
                self.state = "patrol"
        self._gravity(platforms)

    def draw(self, surface, camera_x):
        if not self.alive:
            return
        pos = self._screen_pos(camera_x)
        if not pos:
            return
        x, y = pos
        w, h = self.rect.size
        c = self._color()
        if self.state == "warn" and (self.t // 3) % 2 == 0:
            c = (230, 50, 50)
        pygame.draw.ellipse(surface, c, (x, y + 6, w, h - 6))
        horn_x = x + w - 4 if self.direction > 0 else x + 4
        pygame.draw.polygon(surface, settings.WHITE,
                            [(horn_x, y + 10), (horn_x + 10 * self.direction, y + 2), (horn_x, y + 20)])
        self._eyes(surface, x, y + 4, w, h, angry=True)


# ---------------------------------------------------------------------------
class SpitterEnemy(Enemy):
    """Rooted plant/turret: shoots projectiles at you when you're near."""
    label = "Spitter"

    def __init__(self, x, y, color=(60, 150, 70), shot_color=(140, 255, 90),
                 interval=110, sight=460):
        super().__init__(x, y, 32, 32, x, x + 32, 0, color)
        self.shot_color = shot_color
        self.interval = interval
        self.sight = sight
        self.cool = interval // 2

    def update(self, platforms=None, player=None):
        if not self.alive:
            return
        self._tick()
        self._gravity(platforms)
        if not player:
            return
        dx = player.rect.centerx - self.rect.centerx
        self.direction = 1 if dx > 0 else -1
        self.cool -= 1
        if self.cool <= 0 and abs(dx) < self.sight and abs(player.rect.centery - self.rect.centery) < 140:
            self.cool = self.interval
            self.spawn_queue.append(Projectile(
                self.rect.centerx + 16 * self.direction, self.rect.centery - 4,
                4 * self.direction, 0, self.shot_color, 6, life=140))

    def draw(self, surface, camera_x):
        if not self.alive:
            return
        pos = self._screen_pos(camera_x)
        if not pos:
            return
        x, y = pos
        c = self._color()
        pygame.draw.rect(surface, (80, 60, 50), (x + 6, y + 22, 20, 10), border_radius=3)
        pygame.draw.rect(surface, c, (x + 13, y + 12, 6, 14))
        pygame.draw.circle(surface, c, (x + 16, y + 10), 12)
        mouth_x = x + 16 + 8 * self.direction
        pygame.draw.circle(surface, (40, 10, 20), (mouth_x, y + 10), 6)
        pygame.draw.circle(surface, self.shot_color, (mouth_x, y + 10), 3)
        pygame.draw.circle(surface, settings.WHITE, (x + 16 - 3 * self.direction, y + 5), 3)


# ---------------------------------------------------------------------------
class SpikedEnemy(Enemy):
    """Spiky shell. Jumping on it HURTS. Use an Energy Bolt (X)."""
    stompable = False
    label = "Spiked"

    def __init__(self, x, y, x_min, x_max, speed=1, color=(150, 110, 70)):
        super().__init__(x, y, 34, 30, x_min, x_max, speed, color)

    def draw(self, surface, camera_x):
        if not self.alive:
            return
        pos = self._screen_pos(camera_x)
        if not pos:
            return
        x, y = pos
        c = self._color()
        for i in range(5):
            sx = x + 3 + i * 7
            pygame.draw.polygon(surface, (220, 220, 230), [(sx, y + 12), (sx + 3, y - 4), (sx + 7, y + 12)])
        pygame.draw.ellipse(surface, c, (x, y + 8, 34, 22))
        pygame.draw.circle(surface, settings.WHITE, (x + 17 + 9 * self.direction, y + 18), 4)
        pygame.draw.circle(surface, settings.BLACK, (x + 17 + 10 * self.direction, y + 18), 2)


# ---------------------------------------------------------------------------
class SentinelEnemy(Enemy):
    """Clockwork guardian: heavy armour, takes 2 stomps."""
    label = "Sentinel"

    def __init__(self, x, y, x_min, x_max, speed=2, color=(150, 140, 120)):
        super().__init__(x, y, 36, 42, x_min, x_max, speed, color)
        self.hp = 2

    def draw(self, surface, camera_x):
        if not self.alive:
            return
        pos = self._screen_pos(camera_x)
        if not pos:
            return
        x, y = pos
        c = self._color()
        pygame.draw.rect(surface, (70, 60, 50), (x + 4, y + 30, 10, 12))
        pygame.draw.rect(surface, (70, 60, 50), (x + 22, y + 30, 10, 12))
        pygame.draw.rect(surface, c, (x, y + 12, 36, 22), border_radius=4)
        pygame.draw.rect(surface, c, (x + 6, y, 24, 16), border_radius=4)
        pygame.draw.rect(surface, settings.DARK_GOLD, (x, y + 12, 36, 22), 2, border_radius=4)
        pygame.draw.rect(surface, (255, 80, 60), (x + 10, y + 6, 16, 4))
        # ticking gear
        gx, gy = x + 18, y + 24
        pygame.draw.circle(surface, settings.DARK_GOLD, (gx, gy), 6, 2)
        a = self.t / 8
        pygame.draw.line(surface, settings.DARK_GOLD, (gx, gy), (gx + 6 * math.cos(a), gy + 6 * math.sin(a)), 2)
        if self.hp == 1:
            pygame.draw.line(surface, settings.BLACK, (x + 8, y + 14), (x + 20, y + 30), 2)


# ---------------------------------------------------------------------------
class WraithEnemy(Enemy):
    """Time wraith: drifts through walls toward you. Only Energy Bolts hurt it."""
    stompable = False
    label = "Wraith"

    def __init__(self, x, y, sight=320, color=(120, 80, 200)):
        super().__init__(x, y, 32, 40, x - 60, x + 60, 1, color)
        self.home = (x, y)
        self.sight = sight
        self.hp = 2
        self.fx = float(x)
        self.fy = float(y)

    def update(self, platforms=None, player=None):
        if not self.alive:
            return
        self._tick()
        tx, ty = self.home[0], self.home[1] + math.sin(self.t / 30) * 14
        speed = 0.8
        if player:
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            dist = math.hypot(dx, dy)
            if dist < self.sight:
                tx, ty = player.rect.centerx - 16, player.rect.centery - 20
                speed = 1.5
        vx, vy = tx - self.fx, ty - self.fy
        d = math.hypot(vx, vy) or 1
        if d > 2:
            self.fx += vx / d * speed
            self.fy += vy / d * speed
        self.rect.topleft = (int(self.fx), int(self.fy))
        self.direction = 1 if vx >= 0 else -1

    def draw(self, surface, camera_x):
        if not self.alive:
            return
        pos = self._screen_pos(camera_x)
        if not pos:
            return
        x, y = pos
        ghost = pygame.Surface((44, 56), pygame.SRCALPHA)
        col = (255, 255, 255, 190) if self.flash > 0 else (*self.color, 170)
        pygame.draw.ellipse(ghost, col, (6, 2, 32, 34))
        for i in range(4):
            off = math.sin(self.t / 6 + i) * 3
            pygame.draw.polygon(ghost, col, [(6 + i * 8, 26), (10 + i * 8, 46 + off), (14 + i * 8, 26)])
        pygame.draw.circle(ghost, (255, 240, 120, 255), (16, 16), 3)
        pygame.draw.circle(ghost, (255, 240, 120, 255), (28, 16), 3)
        surface.blit(ghost, (x - 6, y - 2))
