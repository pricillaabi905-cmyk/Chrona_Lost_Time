"""
level2_forest.py - Level 2: Enchanted Forest
Enemies: Forest Frogs (hoppers), Moon Bats, Thorn Spitters, Walkers.
The exit portal is now on solid ground (it used to hang past the edge).
"""

import settings
from src.level import Level
from src.platform import Platform, Spike, Ladder
from src.enemy import Enemy, BatEnemy, HopperEnemy, SpitterEnemy
from src.items import TimeCrystal, Key, Door, EnergyPotion
from src.portal import Portal


def create_level():
    ground = (60, 110, 60)
    bridge = (120, 90, 60)

    platforms = [
        Platform(0, 460, 400, 80, ground),
        Platform(460, 420, 180, 20, bridge),
        Platform(700, 460, 350, 80, ground),
        Platform(600, 320, 140, 20, bridge),
        Platform(850, 280, 100, 20, bridge),
        Platform(1120, 460, 300, 80, ground),
        Platform(1080, 360, 120, 20, bridge),
        Platform(1300, 260, 120, 20, bridge),
        Platform(1500, 460, 1000, 80, ground),
        Platform(1650, 360, 140, 20, bridge),
        Platform(1900, 300, 140, 20, bridge),
    ]
    ladders = [
        Ladder(722, 320, 460),
        Ladder(1350, 260, 460),
        Ladder(1710, 360, 460),
    ]
    spikes = [Spike(400, 440, 60, 20)]

    enemies = [
        Enemy(760, 424, 32, 36, 720, 1020, speed=3, color=settings.GREEN),
        BatEnemy(560, 240, 460, 1000, speed=2),
        HopperEnemy(1150, 430, 1130, 1410, color=(70, 190, 90)),
        SpitterEnemy(1800, 428, color=(100, 60, 140), shot_color=(200, 120, 255)),
        Enemy(1560, 424, 32, 36, 1520, 1780, speed=3, color=settings.GREEN),
        HopperEnemy(1880, 430, 1830, 2100, color=(70, 190, 90)),
        BatEnemy(1560, 220, 1500, 2050, speed=3),
    ]
    crystals = [
        TimeCrystal(630, 280), TimeCrystal(880, 240), TimeCrystal(1330, 220), TimeCrystal(1930, 260),
    ]
    potions = [EnergyPotion(650, 290), EnergyPotion(1330, 230), EnergyPotion(2000, 420)]

    return Level(
        number=2, name="Enchanted Forest", theme_color=ground, sky_color=(120, 180, 150),
        width=2600, player_start=(60, 400), platforms=platforms, spikes=spikes,
        enemies=enemies, crystals=crystals,
        keys=[Key(1150, 420)], doors=[Door(2150, 380, 30, 80)], portal=Portal(2400, 390),
        checkpoints=[(0, 400), (700, 400), (1500, 400)],
        ladders=ladders, potions=potions, bg_style="forest",
    )
