"""
settings.py
-----------
Global constants used across the whole game: screen size, colors,
physics values, key bindings, and file paths.
Keeping these in one place makes the game easy to tune and expand.
"""

import os

# ---------------------------------------------------------------------------
# SCREEN
# ---------------------------------------------------------------------------
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
FPS = 60
GAME_TITLE = "CHRONA: LOST TIME"

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SAVE_FILE = os.path.join(DATA_DIR, "save_game.json")
STORY_FILE = os.path.join(DATA_DIR, "story.json")

# ---------------------------------------------------------------------------
# COLORS  (fantasy palette: violet, blue, gold, dark)
# ---------------------------------------------------------------------------
VIOLET = (107, 76, 239)
LIGHT_VIOLET = (220, 201, 255)
GOLD = (244, 208, 63)
DARK_GOLD = (212, 175, 55)
DARK = (30, 27, 46)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 60, 60)
GREEN = (70, 170, 90)
BLUE = (70, 130, 220)
SKY_BLUE = (140, 190, 230)
BROWN = (110, 80, 55)
SAND = (222, 190, 120)
ICE = (185, 225, 240)
GRAY = (120, 120, 130)
DARK_GRAY = (60, 60, 70)

# ---------------------------------------------------------------------------
# PHYSICS
# ---------------------------------------------------------------------------
GRAVITY = 0.7
MAX_FALL_SPEED = 16
JUMP_STRENGTH = -14
MOVE_SPEED = 5
ICE_FRICTION = 0.94     # slower deceleration on ice platforms
NORMAL_FRICTION = 0.65  # faster deceleration on normal ground

# ---------------------------------------------------------------------------
# PLAYER
# ---------------------------------------------------------------------------
PLAYER_WIDTH = 34
PLAYER_HEIGHT = 52
PLAYER_START_LIVES = 3
PLAYER_INVINCIBLE_TIME = 90  # frames of invincibility after being hit

# ---------------------------------------------------------------------------
# CONTROLS
# ---------------------------------------------------------------------------
import pygame

# Arrow keys AND WASD both work everywhere.
KEYS_LEFT = (pygame.K_LEFT, pygame.K_a)
KEYS_RIGHT = (pygame.K_RIGHT, pygame.K_d)
KEYS_UP = (pygame.K_UP, pygame.K_w)       # jump (or climb up a ladder)
KEYS_DOWN = (pygame.K_DOWN, pygame.K_s)   # climb down a ladder
KEY_JUMP = pygame.K_SPACE                 # always jumps (also jumps off ladders)
KEY_JUMP_ALT = pygame.K_UP                # kept for backward compatibility
KEY_ATTACK = pygame.K_x                   # fire an Energy Bolt
KEY_INTERACT = pygame.K_e                 # enter portal (Enter works too)
KEYS_ENTER_PORTAL = (pygame.K_e, pygame.K_RETURN, pygame.K_KP_ENTER)
KEY_PAUSE = pygame.K_ESCAPE
KEY_HELP = pygame.K_h                     # open How to Play

# Ladders / energy
CLIMB_SPEED = 3
MAX_LIVES = 5
MAX_ENERGY = 100
ENERGY_REGEN = 0.05        # per frame (about 3 per second)
BOLT_COST = 25
BOLT_COOLDOWN = 18
POTION_ENERGY = 50

# Jump feel: forgiving input so a slightly-early or slightly-late press
# still registers, which fixes most "jump doesn't work" complaints.
COYOTE_TIME_FRAMES = 7   # can still jump for a few frames after leaving a ledge
JUMP_BUFFER_FRAMES = 7   # a jump press just before landing still fires

# ---------------------------------------------------------------------------
# GAME STATES
# ---------------------------------------------------------------------------
STATE_MENU = "menu"
STATE_LEVEL_MAP = "level_map"
STATE_SETTINGS = "settings"
STATE_PLAYING = "playing"
STATE_DIALOGUE = "dialogue"
STATE_PAUSE = "pause"
STATE_GAME_OVER = "game_over"
STATE_LEVEL_COMPLETE = "level_complete"
STATE_WIN = "win"
STATE_HOWTO = "howto"

TOTAL_LEVELS = 5

# ---------------------------------------------------------------------------
# BOSS FIGHT (Level 5 climax)
# ---------------------------------------------------------------------------
BOSS_NAME = "The Hollow Sovereign"
BOSS_MONSTER_NAME = "The Timewyrm"
BOSS_MAX_HP = 3
VILLAIN_VIOLET = (70, 20, 90)
VILLAIN_RED = (170, 30, 50)
MONSTER_COLOR = (60, 10, 40)
