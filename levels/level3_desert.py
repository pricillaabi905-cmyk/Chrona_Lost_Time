"""
level3_desert.py - Level 3: Desert Kingdom
Enemies: Sand Chargers (rush you!), Spiked Cactus Crawlers (shoot them - never stomp),
Dust Bats, Cactus Spitters. Idris the Shade duels you near the end.
"""

import settings
from src.level import Level
from src.platform import Platform, Spike, Ladder
from src.enemy import BatEnemy, ChargerEnemy, SpikedEnemy, SpitterEnemy
from src.items import TimeCrystal, EnergyPotion
from src.portal import Portal
from src.rival import create_idris


def create_level():
    sand = settings.SAND
    stone = (170, 140, 90)

    platforms = [
        Platform(0, 460, 450, 80, sand),
        Platform(500, 400, 120, 20, stone),
        Platform(680, 340, 120, 20, stone),
        Platform(860, 460, 350, 80, sand),
        Platform(950, 380, 100, 20, stone),
        Platform(1150, 300, 100, 20, stone),
        Platform(1350, 460, 300, 80, sand),
        Platform(1450, 380, 300, 20, stone),
        Platform(1750, 460, 1150, 80, sand),
        Platform(1900, 340, 140, 20, stone),
        Platform(2150, 260, 140, 20, stone),
    ]
    ladders = [
        Ladder(1190, 300, 460),
        Ladder(1550, 380, 460),
        Ladder(2200, 260, 460),
    ]
    spikes = [Spike(450, 440, 50, 20), Spike(1210, 440, 60, 20), Spike(1700, 440, 50, 20)]

    enemies = [
        ChargerEnemy(900, 424, 870, 1190),
        SpikedEnemy(1400, 428, 1360, 1640),
        BatEnemy(520, 250, 480, 1100, speed=2),
        BatEnemy(1450, 220, 1400, 1950, speed=3),
        SpitterEnemy(2450, 428, color=(70, 140, 60), shot_color=(255, 230, 100)),
        ChargerEnemy(2560, 424, 2500, 2800, color=(200, 90, 50)),
    ]
    crystals = [
        TimeCrystal(530, 360), TimeCrystal(710, 300), TimeCrystal(980, 340),
        TimeCrystal(1180, 260), TimeCrystal(2180, 220),
    ]
    potions = [EnergyPotion(1200, 270), EnergyPotion(1620, 350), EnergyPotion(2220, 230)]

    level = Level(
        number=3, name="Desert Kingdom", theme_color=stone, sky_color=(250, 220, 150),
        width=2950, player_start=(60, 400), platforms=platforms, spikes=spikes,
        enemies=enemies, crystals=crystals, portal=Portal(2800, 390),
        checkpoints=[(0, 400), (860, 400), (1750, 400)],
        ladders=ladders, potions=potions, bg_style="desert",
    )
    idris = create_idris(x=1950, y=424, patrol_min=1780, patrol_max=2320)
    level.add_rival(idris, trigger_x=1800)
    return level
