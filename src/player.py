"""
player.py
---------
Defines Aria, the main playable character.

Since this project uses no external art files, Aria is drawn with simple
shapes (a small "vector sprite") in her signature violet / white / gold
color scheme. This keeps the game runnable with zero external assets
while leaving a clear place to swap in real sprite images later
(see the `draw()` method).
"""

import pygame
import settings
from src.asset_loader import get_sprite


class Player:
    def __init__(self, x, y):
        self.width = settings.PLAYER_WIDTH
        self.height = settings.PLAYER_HEIGHT
        self.rect = pygame.Rect(x, y, self.width, self.height)

        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True

        self.lives = settings.PLAYER_START_LIVES
        self.crystals = 0
        self.has_key = False

        self.invincible_timer = 0
        self.spawn_point = (x, y)

        # simple walk-cycle animation timer (bob effect, no sprite sheet needed)
        self.anim_timer = 0
        self.is_walking = False

        # --- forgiving jump feel: coyote time + jump buffering ---
        # coyote_timer: counts down while the player is airborne after
        #   walking off a ledge; a jump press still works during this window.
        # jump_buffer_timer: counts down after a jump press; if the player
        #   lands on ground before this expires, the jump fires anyway.
        self.coyote_timer = 0
        self.jump_buffer_timer = 0

        # --- energy + Energy Bolt ---
        self.energy = float(settings.MAX_ENERGY)
        self.bolt_cooldown = 0

        # --- ladder climbing ---
        self.on_ladder = False
        self.ladder = None
        self.is_climbing = False

    # ------------------------------------------------------------------
    # ENERGY / POTIONS / BOLT
    # ------------------------------------------------------------------
    def drink_potion(self):
        """Energy Potion: +energy. If energy was already full, heal 1 life."""
        if self.energy >= settings.MAX_ENERGY - 1:
            if self.lives < settings.MAX_LIVES:
                self.lives += 1
        self.energy = min(settings.MAX_ENERGY, self.energy + settings.POTION_ENERGY)

    def fire_bolt(self):
        """Returns a new Energy Bolt Projectile, or None if not enough energy."""
        from src.projectile import Projectile
        if self.bolt_cooldown > 0 or self.energy < settings.BOLT_COST:
            return None
        self.energy -= settings.BOLT_COST
        self.bolt_cooldown = settings.BOLT_COOLDOWN
        d = 1 if self.facing_right else -1
        return Projectile(self.rect.centerx + 22 * d, self.rect.centery - 6,
                          9 * d, 0, (255, 255, 255), 6, from_player=True, life=70)

    # ------------------------------------------------------------------
    # LADDERS
    # ------------------------------------------------------------------
    def _ladder_at(self, ladders):
        cx = self.rect.centerx
        for lad in ladders:
            r = lad.rect
            if r.left <= cx <= r.right and self.rect.bottom >= r.top - 2 and self.rect.top <= r.bottom:
                return lad
        return None

    def try_grab_ladder(self, ladders, going_up):
        """Grab a ladder if one is in front of us. UP needs feet below the top
        (so you don't re-grab when you just climbed off); DOWN works from the
        top edge or mid-ladder but not at the very bottom."""
        lad = self._ladder_at(ladders)
        if not lad:
            return False
        if going_up and self.rect.bottom <= lad.rect.top + 6:
            return False
        if not going_up and self.rect.bottom >= lad.rect.bottom - 4:
            return False
        self.on_ladder = True
        self.ladder = lad
        self.rect.centerx = lad.rect.centerx
        self.vel_x = 0
        self.vel_y = 0
        return True

    def leave_ladder(self):
        self.on_ladder = False
        self.ladder = None
        self.is_climbing = False

    def climb(self, keys):
        """Movement while on a ladder (replaces normal physics)."""
        lad = self.ladder
        dy = 0
        if any(keys[k] for k in settings.KEYS_UP):
            dy = -settings.CLIMB_SPEED
        if any(keys[k] for k in settings.KEYS_DOWN):
            dy = settings.CLIMB_SPEED
        self.is_climbing = dy != 0
        self.rect.y += dy
        self.vel_x = self.vel_y = 0
        self.on_ground = False
        if any(keys[k] for k in settings.KEYS_LEFT):
            self.rect.x -= 2
            self.facing_right = False
        if any(keys[k] for k in settings.KEYS_RIGHT):
            self.rect.x += 2
            self.facing_right = True

        if self.rect.bottom <= lad.rect.top:          # reached the top
            self.rect.bottom = lad.rect.top
            self.leave_ladder()
            self.on_ground = True
        elif self.rect.bottom >= lad.rect.bottom:     # reached the bottom
            self.rect.bottom = lad.rect.bottom
            self.leave_ladder()
            self.on_ground = True
        elif not (lad.rect.left <= self.rect.centerx <= lad.rect.right):
            self.leave_ladder()                       # stepped off sideways

    def jump_off_ladder(self):
        self.leave_ladder()
        self.vel_y = settings.JUMP_STRENGTH * 0.75
        self.on_ground = False

    # ------------------------------------------------------------------
    # UPDATE / PHYSICS
    # ------------------------------------------------------------------
    def handle_input(self, keys):
        self.vel_x = 0
        self.is_walking = False
        if any(keys[k] for k in settings.KEYS_LEFT):
            self.vel_x = -settings.MOVE_SPEED
            self.facing_right = False
            self.is_walking = True
        if any(keys[k] for k in settings.KEYS_RIGHT):
            self.vel_x = settings.MOVE_SPEED
            self.facing_right = True
            self.is_walking = True

    def request_jump(self):
        """Call this whenever the jump key is pressed (KEYDOWN). It doesn't
        jump immediately - it just starts the buffer window so the actual
        jump can fire this frame or a few frames from now once grounded."""
        self.jump_buffer_timer = settings.JUMP_BUFFER_FRAMES

    def try_consume_jump(self):
        """Call this once per frame (after physics). If a jump was recently
        requested AND the player is grounded or still within coyote time,
        perform the jump and clear both timers."""
        if self.jump_buffer_timer > 0 and (self.on_ground or self.coyote_timer > 0):
            self.vel_y = settings.JUMP_STRENGTH
            self.on_ground = False
            self.jump_buffer_timer = 0
            self.coyote_timer = 0

    def jump(self):
        """Direct/instant jump, kept for backward compatibility and for
        simple scripted/test scenarios."""
        if self.on_ground or self.coyote_timer > 0:
            self.vel_y = settings.JUMP_STRENGTH
            self.on_ground = False
            self.coyote_timer = 0

    def apply_gravity(self):
        self.vel_y += settings.GRAVITY
        if self.vel_y > settings.MAX_FALL_SPEED:
            self.vel_y = settings.MAX_FALL_SPEED

    def move_and_collide(self, platforms):
        """Move the player and resolve collisions with a list of Platform
        objects, axis by axis, so sliding along walls/floors feels smooth."""

        # --- Horizontal movement ---
        self.rect.x += self.vel_x
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel_x > 0:
                    self.rect.right = plat.rect.left
                elif self.vel_x < 0:
                    self.rect.left = plat.rect.right

        # --- Vertical movement ---
        was_on_ground = self.on_ground
        self.apply_gravity()
        self.rect.y += self.vel_y
        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel_y > 0:
                    self.rect.bottom = plat.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    if getattr(plat, "is_ice", False):
                        self.vel_x *= settings.ICE_FRICTION
                elif self.vel_y < 0:
                    self.rect.top = plat.rect.bottom
                    self.vel_y = 0

        if self.on_ground:
            self.coyote_timer = settings.COYOTE_TIME_FRAMES
        elif was_on_ground:
            # just walked off a ledge - coyote window starts now
            self.coyote_timer = settings.COYOTE_TIME_FRAMES
        elif self.coyote_timer > 0:
            self.coyote_timer -= 1

        # Resolve any buffered/queued jump now that collisions are settled
        self.try_consume_jump()

    def take_damage(self, amount=1, knockback_dir=0):
        if self.invincible_timer > 0:
            return
        self.lives -= amount
        self.leave_ladder()
        self.invincible_timer = settings.PLAYER_INVINCIBLE_TIME
        self.vel_y = -8
        self.vel_x = 6 * knockback_dir

    def update_timers(self):
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= 1
        if self.bolt_cooldown > 0:
            self.bolt_cooldown -= 1
        self.energy = min(settings.MAX_ENERGY, self.energy + settings.ENERGY_REGEN)
        self.anim_timer += 1

    def respawn_at_checkpoint(self):
        self.rect.x, self.rect.y = self.spawn_point
        self.vel_x = 0
        self.vel_y = 0
        self.leave_ladder()
        self.invincible_timer = settings.PLAYER_INVINCIBLE_TIME

    def is_alive(self):
        return self.lives > 0

    # ------------------------------------------------------------------
    # DRAW
    # ------------------------------------------------------------------
    def draw(self, surface, camera_x):
        x = self.rect.x - camera_x
        y = self.rect.y

        # Blink while invincible
        if self.invincible_timer > 0 and (self.invincible_timer // 5) % 2 == 0:
            return

        # Use a real sprite image if the user has added one; otherwise
        # fall back to the procedurally-drawn character below.
        sprite = get_sprite("aria", target_size=(self.width + 12, self.height + 8))
        if sprite:
            if not self.facing_right:
                sprite = pygame.transform.flip(sprite, True, False)
            surface.blit(sprite, (x - 6, y - 4))
            return

        bob = 2 if ((self.is_walking or self.is_climbing) and (self.anim_timer // 6) % 2 == 0) else 0
        if self.on_ladder:
            # arms reaching up to the rungs
            arm = 6 if (self.anim_timer // 8) % 2 == 0 else 0
            pygame.draw.rect(surface, (255, 224, 196), (x - 2, y + 4 + arm, 5, 14))
            pygame.draw.rect(surface, (255, 224, 196), (x + self.width - 3, y + 10 - arm, 5, 14))

        # Cape (violet, behind body)
        cape_points = [
            (x + self.width // 2, y + 6),
            (x - 4, y + self.height),
            (x + self.width + 4, y + self.height),
        ]
        pygame.draw.polygon(surface, settings.VIOLET, cape_points)

        # Legs (dark boots)
        pygame.draw.rect(surface, settings.DARK, (x + 6, y + 34 + bob, 8, 18))
        pygame.draw.rect(surface, settings.DARK, (x + self.width - 14, y + 34 + bob, 8, 18))

        # Body (white/violet tunic)
        pygame.draw.rect(surface, settings.WHITE, (x + 4, y + 16 + bob, self.width - 8, 22))
        pygame.draw.rect(surface, settings.VIOLET, (x + 4, y + 16 + bob, self.width - 8, 6))

        # Belt with hourglass crystal
        pygame.draw.rect(surface, settings.DARK_GOLD, (x + 4, y + 30 + bob, self.width - 8, 4))
        pygame.draw.circle(surface, settings.GOLD, (x + self.width // 2, y + 32 + bob), 3)

        # Head
        pygame.draw.circle(surface, (255, 224, 196), (x + self.width // 2, y + 10), 10)

        # Long black hair
        pygame.draw.ellipse(surface, settings.DARK, (x + 2, y - 2, self.width - 4, 18))
        pygame.draw.rect(surface, settings.DARK, (x + 2, y + 4, 6, 16))
        pygame.draw.rect(surface, settings.DARK, (x + self.width - 8, y + 4, 6, 16))

        # Facing indicator (small gold gem on the front side)
        gem_x = x + self.width - 8 if self.facing_right else x + 2
        pygame.draw.circle(surface, settings.GOLD, (gem_x, y + 24 + bob), 2)

    def draw_shadow(self, surface, camera_x):
        x = self.rect.centerx - camera_x
        y = self.rect.bottom
        pygame.draw.ellipse(surface, (0, 0, 0, 60), (x - 12, y - 4, 24, 6))
