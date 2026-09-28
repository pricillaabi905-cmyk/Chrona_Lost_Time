"""
level1_temple.py - Level 1: Ancient Temple
Enemies: Walkers, Temple Bats, Stone Hoppers, a Thorn Spitter guarding the portal.
New here: LADDERS (3) and ENERGY POTIONS.
"""

import settings
from src.level import Level
from src.platform import Platform, Spike, Ladder
from src.enemy import Enemy, BatEnemy, HopperEnemy, SpitterEnemy
from src.items import TimeCrystal, EnergyPotion
from src.portal import Portal


def create_level():
    ground = settings.BROWN
    stone = settings.GRAY

    platforms = [
        Platform(0, 460, 500, 80, ground),
        Platform(560, 460, 300, 80, ground),
        Platform(300, 360, 140, 24, stone),
        Platform(560, 300, 140, 24, stone),
        Platform(900, 460, 500, 80, ground),
        Platform(760, 380, 120, 24, stone),
        Platform(1000, 340, 160, 24, stone),
        Platform(1250, 460, 600, 80, ground),
        Platform(1350, 360, 120, 24, stone),
        Platform(1550, 280, 140, 24, stone),
        Platform(1750, 460, 500, 80, ground),
        Platform(1800, 230, 180, 24, stone),        # high ledge (ladder!)
    ]
    ladders = [
        Ladder(400, 360, 460),      # ground -> first stone ledge
        Ladder(1110, 340, 460),     # ground -> ledge above the middle
        Ladder(1860, 230, 460),     # tall ladder to the treasure ledge
    ]
    spikes = [Spike(500, 440, 60, 20), Spike(1180, 440, 70, 20)]

    enemies = [
        Enemy(620, 424, 30, 36, 600, 840, speed=2, color=settings.RED),
        BatEnemy(880, 260, 780, 1150),
        HopperEnemy(1300, 430, 1260, 1560, color=(120, 130, 150)),
        Enemy(1850, 424, 30, 36, 1780, 2100, speed=2, color=settings.RED),
        SpitterEnemy(2110, 428),
    ]
    crystals = [
        TimeCrystal(360, 320), TimeCrystal(610, 260), TimeCrystal(1020, 300),
        TimeCrystal(1600, 240), TimeCrystal(1850, 190), TimeCrystal(1920, 190),
    ]
    potions = [EnergyPotion(340, 330), EnergyPotion(1880, 200), EnergyPotion(1250, 430)]

    return Level(
        number=1, name="Ancient Temple", theme_color=stone, sky_color=(70, 60, 90),
        width=2300, player_start=(60, 400), platforms=platforms, spikes=spikes,
        enemies=enemies, crystals=crystals, portal=Portal(2200, 390),
        checkpoints=[(0, 400), (900, 400), (1750, 400)],
        ladders=ladders, potions=potions, bg_style="temple",
    )
