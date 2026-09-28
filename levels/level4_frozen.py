"""
level4_frozen.py - Level 4: Frozen Kingdom
Enemies: Frost Slimes (hoppers), Frost Beasts (chargers), Ice Turrets (spitters),
Frost Bats, Spiked Ice Crawlers. Rowan of the Ice Court duels you.
"""

import settings
from src.level import Level
from src.platform import Platform, Spike, Ladder
from src.enemy import BatEnemy, HopperEnemy, ChargerEnemy, SpitterEnemy, SpikedEnemy
from src.items import TimeCrystal, EnergyPotion
from src.portal import Portal
from src.rival import create_rowan


def create_level():
    ice = settings.ICE
    snow = (230, 240, 250)

    platforms = [
        Platform(0, 460, 400, 80, snow),
        Platform(450, 420, 160, 20, ice, is_ice=True),
        Platform(670, 360, 160, 20, ice, is_ice=True),
        Platform(900, 460, 300, 80, snow),
        Platform(950, 320, 200, 20, ice, is_ice=True),
        Platform(1260, 460, 300, 80, snow),
        Platform(1300, 380, 160, 20, ice, is_ice=True),
        Platform(1500, 300, 200, 20, ice, is_ice=True),
        Platform(1800, 460, 1100, 80, snow),
        Platform(1950, 360, 200, 20, ice, is_ice=True),
    ]
    ladders = [
        Ladder(1000, 320, 460),
        Ladder(1530, 300, 460),
        Ladder(2000, 360, 460),
    ]
    spikes = [Spike(400, 440, 50, 20), Spike(1200, 440, 60, 20)]

    enemies = [
        BatEnemy(480, 270, 440, 850, speed=2, color=(120, 160, 210)),
        HopperEnemy(930, 430, 910, 1190, color=(150, 210, 240)),
        SpitterEnemy(1150, 428, color=(140, 200, 230), shot_color=(200, 240, 255)),
        ChargerEnemy(1300, 424, 1270, 1550, color=(140, 170, 210)),
        BatEnemy(1350, 230, 1300, 1800, speed=3, color=(120, 160, 210)),
        SpikedEnemy(2450, 428, 2420, 2650, color=(120, 170, 200)),
        HopperEnemy(2700, 430, 2660, 2860, color=(150, 210, 240)),
    ]
    crystals = [
        TimeCrystal(510, 380), TimeCrystal(730, 320), TimeCrystal(1030, 280),
        TimeCrystal(1610, 260), TimeCrystal(2020, 320),
    ]
    potions = [EnergyPotion(520, 390), EnergyPotion(1040, 290), EnergyPotion(1560, 270),
               EnergyPotion(2040, 330)]

    level = Level(
        number=4, name="Frozen Kingdom", theme_color=ice, sky_color=(200, 220, 240),
        width=3000, player_start=(60, 400), platforms=platforms, spikes=spikes,
        enemies=enemies, crystals=crystals, portal=Portal(2820, 390),
        checkpoints=[(0, 400), (900, 400), (1800, 400)],
        ladders=ladders, potions=potions, bg_style="ice",
    )
    rowan = create_rowan(x=2050, y=424, patrol_min=1830, patrol_max=2370)
    level.add_rival(rowan, trigger_x=1850)
    return level
