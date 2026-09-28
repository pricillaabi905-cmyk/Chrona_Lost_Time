"""
level.py
--------
The Level class holds all the objects that make up a playable level:
platforms, spikes, enemies, crystals, keys/doors, the portal, the
background theme, and checkpoints. Individual level layouts (Temple,
Forest, Desert, Frozen Kingdom, Royal Castle) are defined in the
`levels/` folder and each build one of these Level objects.
"""

import math
import pygame
import settings
from src.player import Player


class Level:
    def __init__(self, number, name, theme_color, sky_color, width,
                 player_start, platforms, spikes=None, enemies=None,
                 crystals=None, keys=None, doors=None, portal=None,
                 checkpoints=None, decorations=None,
                 boss=None, boss_trigger_x=None,
                 ladders=None, potions=None, bg_style="temple"):
        self.number = number
        self.name = name
        self.theme_color = theme_color
        self.sky_color = sky_color
        self.width = width  # total level width in pixels (for camera bounds)

        self.player_start = player_start
        self.platforms = platforms
        self.spikes = spikes or []
        self.enemies = enemies or []
        self.crystals = crystals or []
        self.keys = keys or []
        self.doors = doors or []
        self.portal = portal
        self.checkpoints = checkpoints or []  # list of (x, y) points, left-to-right
        self.decorations = decorations or []  # purely visual shapes

        self.ladders = ladders or []
        self.potions = potions or []
        self.bg_style = bg_style
        self.projectiles = []      # enemy shots that can hurt the player
        self.player_bolts = []     # the player's Energy Bolts
        self.frame = 0

        self.crystals_collected_this_level = 0
        self.completed = False

        # --- Boss fight (currently only used by Level 5) ---
        self.boss = boss
        self.boss_trigger_x = boss_trigger_x
        self.boss_active = False
        self.boss_intro_played = False
        self.boss_victory_played = False
        if self.boss and self.portal:
            self.portal.active = False  # sealed until the boss is defeated

        # --- Rival prince duels (Levels 3 and 4) ---
        # Each entry: {"unit": RivalPrince, "trigger_x": int,
        #              "intro_played": bool, "active": bool, "victory_played": bool}
        self.rivals = []

    def add_rival(self, unit, trigger_x):
        self.rivals.append({
            "unit": unit,
            "trigger_x": trigger_x,
            "intro_played": False,
            "active": False,
            "victory_played": False,
        })

    def check_rival_trigger(self, player):
        """Returns the rival dict that should start its intro dialogue now,
        or None."""
        for rival in self.rivals:
            if not rival["intro_played"] and player.rect.centerx >= rival["trigger_x"]:
                return rival
        return None

    def check_rival_victory(self):
        """Returns the rival dict that just got defeated and needs its
        victory dialogue shown, or None."""
        for rival in self.rivals:
            if rival["active"] and rival["unit"].defeated and not rival["victory_played"]:
                return rival
        return None

    def make_player(self):
        p = Player(*self.player_start)
        p.spawn_point = self.player_start
        return p

    def update_checkpoint(self, player):
        for cp in self.checkpoints:
            if player.rect.x >= cp[0]:
                player.spawn_point = cp

    def get_camera_x(self, player):
        camera_x = player.rect.centerx - settings.SCREEN_WIDTH // 2
        camera_x = max(0, min(camera_x, max(0, self.width - settings.SCREEN_WIDTH)))
        return camera_x

    def add_bolt(self, bolt):
        if bolt:
            self.player_bolts.append(bolt)

    def update(self, player, keys_pressed):
        self.frame += 1
        for enemy in self.enemies:
            enemy.update(self.platforms, player)
            enemy.check_player_collision(player)
            if enemy.spawn_queue:
                self.projectiles.extend(enemy.spawn_queue)
                enemy.spawn_queue.clear()

        # enemy projectiles -> player
        for proj in self.projectiles:
            proj.update()
            if any(proj.rect.colliderect(p.rect) for p in self.platforms):
                proj.alive = False
            elif proj.rect.colliderect(player.rect) and player.invincible_timer == 0:
                player.take_damage(1, knockback_dir=1 if proj.vx > 0 else -1)
                proj.alive = False
        self.projectiles = [p for p in self.projectiles if p.alive]

        # player Energy Bolts -> enemies
        for bolt in self.player_bolts:
            bolt.update()
            if any(bolt.rect.colliderect(p.rect) for p in self.platforms):
                bolt.alive = False
                continue
            for enemy in self.enemies:
                if enemy.alive and bolt.rect.colliderect(enemy.rect):
                    enemy.take_bolt()
                    bolt.alive = False
                    break
        self.player_bolts = [b for b in self.player_bolts if b.alive]

        for potion in self.potions:
            potion.update()
            potion.check_collected(player)

        for crystal in self.crystals:
            crystal.update()
            if crystal.check_collected(player):
                self.crystals_collected_this_level += 1

        for key_item in self.keys:
            key_item.check_collected(player)

        for door in self.doors:
            door.update(player)
            if door.blocks(player):
                # simple block: push the player back out
                if player.vel_x > 0:
                    player.rect.right = door.rect.left
                elif player.vel_x < 0:
                    player.rect.left = door.rect.right

        for spike in self.spikes:
            if player.invincible_timer == 0 and player.rect.colliderect(spike.rect):
                player.take_damage(1, knockback_dir=-1 if player.facing_right else 1)

        self.update_checkpoint(player)

        if self.boss and self.boss_active and self.boss.alive:
            self.boss.update(player)
            self.boss.check_player_collision(player)

        for rival in self.rivals:
            if rival["active"] and rival["unit"].alive:
                rival["unit"].update(self.platforms)
                rival["unit"].check_player_collision(player)

        # Fall off the world = damage + respawn
        if player.rect.top > 2000:
            player.take_damage(1)
            player.respawn_at_checkpoint()

    def player_reached_boss_trigger(self, player):
        return (self.boss is not None and not self.boss_intro_played
                and self.boss_trigger_x is not None
                and player.rect.centerx >= self.boss_trigger_x)

    def draw_background(self, surface, camera_x):
        """Sky colour + simple parallax scenery that depends on the world."""
        surface.fill(self.sky_color)
        sky = self.sky_color
        far_col = tuple(max(0, c - 28) for c in sky)
        near_col = tuple(max(0, c - 55) for c in sky)
        style = self.bg_style
        W, H = settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT
        far = int(camera_x * 0.25)
        near = int(camera_x * 0.5)

        if style == "desert":
            pygame.draw.circle(surface, (255, 180, 90), (700, 110), 60)
            pygame.draw.circle(surface, (255, 220, 140), (700, 110), 40)
        if style == "castle":
            pygame.draw.circle(surface, (230, 220, 255), (200, 90), 36)
            pygame.draw.circle(surface, sky, (214, 82), 32)

        # far layer
        for i in range(-1, W // 220 + 3):
            bx = i * 220 - far % 220
            n = (i + far // 220)
            hh = 90 + (n * 37) % 70
            if style == "ice":
                pygame.draw.polygon(surface, far_col, [(bx, 420), (bx + 110, 420 - hh - 30), (bx + 220, 420)])
            elif style == "desert":
                pygame.draw.ellipse(surface, far_col, (bx - 40, 420 - hh // 2, 300, hh))
            elif style == "forest":
                pygame.draw.polygon(surface, far_col, [(bx + 20, 430), (bx + 110, 430 - hh - 40), (bx + 200, 430)])
            elif style == "castle":
                pygame.draw.rect(surface, far_col, (bx + 40, 430 - hh - 40, 60, hh + 40))
                pygame.draw.polygon(surface, far_col, [(bx + 32, 430 - hh - 40), (bx + 70, 430 - hh - 90), (bx + 108, 430 - hh - 40)])
            else:  # temple
                pygame.draw.rect(surface, far_col, (bx + 60, 430 - hh, 34, hh))
                pygame.draw.rect(surface, far_col, (bx + 50, 430 - hh - 8, 54, 10))

        # near layer
        for i in range(-1, W // 170 + 3):
            bx = i * 170 - near % 170
            n = (i + near // 170)
            hh = 50 + (n * 53) % 60
            if style == "ice":
                pygame.draw.polygon(surface, near_col, [(bx, 470), (bx + 40, 470 - hh), (bx + 80, 470)])
            elif style == "desert":
                pygame.draw.polygon(surface, near_col, [(bx, 470), (bx + 85, 470 - hh // 2), (bx + 170, 470)])
            elif style == "forest":
                pygame.draw.rect(surface, (50, 40, 30), (bx + 70, 470 - hh, 12, hh))
                pygame.draw.circle(surface, near_col, (bx + 76, 470 - hh), 34)
            elif style == "castle":
                pygame.draw.rect(surface, near_col, (bx + 20, 470 - hh, 26, hh))
                pygame.draw.rect(surface, near_col, (bx + 16, 470 - hh - 6, 34, 8))
            else:
                pygame.draw.rect(surface, near_col, (bx + 30, 470 - hh, 18, hh))

        # drifting particles: snow / fireflies / embers
        t = self.frame
        if style == "ice":
            for k in range(40):
                px = (k * 97 + t * (1 + k % 3) * 0.6) % W
                py = (k * 53 + t * (1 + k % 2)) % H
                pygame.draw.circle(surface, (255, 255, 255), (int(px), int(py)), 2)
        elif style == "forest":
            for k in range(14):
                px = (k * 131 + math.sin(t / 40 + k) * 30) % W
                py = 200 + (k * 41) % 240 + math.sin(t / 30 + k) * 15
                pygame.draw.circle(surface, (255, 240, 120), (int(px), int(py)), 3)
        elif style == "castle":
            for k in range(16):
                px = (k * 89 + math.sin(t / 50 + k) * 20) % W
                py = (H - (t * (1 + k % 3) * 0.7 + k * 37)) % H
                pygame.draw.circle(surface, (190, 120, 255), (int(px), int(py)), 2)
        for deco in self.decorations:
            if hasattr(deco, "draw"):
                deco.draw(surface, camera_x)

    def draw(self, surface, camera_x):
        self.draw_background(surface, camera_x)
        for plat in self.platforms:
            plat.draw(surface, camera_x)
        for ladder in self.ladders:
            ladder.draw(surface, camera_x)
        for spike in self.spikes:
            spike.draw(surface, camera_x)
        for door in self.doors:
            door.draw(surface, camera_x)
        for key_item in self.keys:
            key_item.draw(surface, camera_x)
        for crystal in self.crystals:
            crystal.draw(surface, camera_x)
        for potion in self.potions:
            potion.draw(surface, camera_x)
        for enemy in self.enemies:
            enemy.draw(surface, camera_x)
        for proj in self.projectiles + self.player_bolts:
            proj.draw(surface, camera_x)
        for rival in self.rivals:
            rival["unit"].draw(surface, camera_x)
        if self.boss:
            self.boss.draw(surface, camera_x)
        if self.portal:
            self.portal.draw(surface, camera_x)
