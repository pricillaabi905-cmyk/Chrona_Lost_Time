"""
level5_castle.py - Level 5: Dragon's Sanctum (final level)
Enemies: Clockwork Sentinels (2 stomps), Time Wraiths (only Energy Bolts hurt them),
Chargers, Spiked Crawlers, Spitters, Bats, then the Timewyrm boss.
"""

import settings
from src.level import Level
from src.platform import Platform, Spike, Ladder
from src.enemy import (BatEnemy, ChargerEnemy, SpikedEnemy, SpitterEnemy,
                       SentinelEnemy, WraithEnemy)
from src.items import TimeCrystal, Key, Door, EnergyPotion
from src.portal import Portal
from src.boss import TimewyrmBoss


def create_level():
    stone = (90, 70, 110)
    gold = settings.DARK_GOLD

    platforms = [
        Platform(0, 460, 350, 80, stone),
        Platform(420, 400, 100, 20, gold),
        Platform(600, 340, 100, 20, gold),
        Platform(780, 460, 300, 80, stone),
        Platform(850, 380, 100, 20, gold),
        Platform(1050, 300, 100, 20, gold),
        Platform(1250, 460, 300, 80, stone),
        Platform(1300, 380, 300, 20, gold),
        Platform(1650, 460, 250, 80, stone),
        Platform(1750, 340, 120, 20, gold),
        Platform(1950, 260, 120, 20, gold),
        Platform(2150, 460, 900, 80, stone),
        Platform(2300, 360, 200, 20, gold),
    ]
    ladders = [
        Ladder(1065, 300, 460),
        Ladder(1400, 380, 460),
        Ladder(1810, 340, 460),
        Ladder(2400, 360, 460),
    ]
    spikes = [Spike(350, 440, 70, 20), Spike(1080, 440, 60, 20),
              Spike(1550, 440, 60, 20), Spike(1900, 440, 60, 20)]

    purple = (140, 40, 160)
    enemies = [
        BatEnemy(560, 250, 430, 780, speed=3, color=purple),
        SentinelEnemy(880, 418, 800, 1060),
        WraithEnemy(1180, 300),
        SpitterEnemy(1500, 428, color=(90, 40, 120), shot_color=(230, 120, 255)),
        ChargerEnemy(1320, 424, 1260, 1480, color=purple),
        SpikedEnemy(1700, 430, 1660, 1880, color=(90, 70, 100)),
        WraithEnemy(1850, 230),
        SentinelEnemy(2200, 418, 2160, 2600),
        BatEnemy(2200, 240, 2160, 2600, speed=3, color=purple),
    ]
    crystals = [
        TimeCrystal(450, 360), TimeCrystal(630, 300), TimeCrystal(1080, 260),
        TimeCrystal(1980, 220), TimeCrystal(2380, 320),
    ]
    potions = [EnergyPotion(460, 370), EnergyPotion(1100, 270), EnergyPotion(1330, 350),
               EnergyPotion(2330, 330), EnergyPotion(2600, 430)]

    boss = TimewyrmBoss(x=2680, y=390, patrol_min=2660, patrol_max=2850)

    return Level(
        number=5, name="Dragon's Sanctum", theme_color=stone, sky_color=(45, 30, 70),
        width=3050, player_start=(60, 400), platforms=platforms, spikes=spikes,
        enemies=enemies, crystals=crystals,
        keys=[Key(1290, 340)], doors=[Door(2100, 380, 30, 80)], portal=Portal(2900, 390),
        checkpoints=[(0, 400), (780, 400), (1650, 400), (2150, 400), (2650, 400)],
        boss=boss, boss_trigger_x=2620,
        ladders=ladders, potions=potions, bg_style="castle",
    )
