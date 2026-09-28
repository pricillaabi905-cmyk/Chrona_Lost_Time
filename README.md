# Chrona: Lost Time

A small original 2D side-scrolling platform adventure built with **Python + Pygame**.

You play as **Aria**, a princess who flees her palace rather than marry a
man she doesn't love, choosing to live as a warrior instead. She doesn't
yet know she carries real power of her own. On the road she collides
(literally - he pulls her into a river thinking she's an assassin) with
**Caleb**, a guarded stranger hunting a legendary dragon's crystal heart.
What starts as a wary, prickly rivalry turns into something else as they
travel together - and Caleb turns out to be hiding a much bigger secret
than either of them expected.

Along the way, two rival princes sent to stop them - **Idris the Shade**
and **Rowan of the Ice Court** - are defeated in duels but not destroyed,
and end up switching sides for the final confrontation with the true
villain, **The Hollow Sovereign**, and his monster, **The Timewyrm**.

## Controls (arrow keys AND WASD both work)
| Action | Keys |
|--------|------|
| Walk left / right | Left / Right Arrow  (or A / D) |
| Jump | Space, or Up Arrow (W) |
| Climb a ladder | Stand at it and press Up / Down (W / S) - Space jumps off |
| Energy Bolt | X (costs 25 energy) |
| Enter the portal | Enter (or E) when standing at the glowing portal |
| Pause | Escape |
| How to Play screen | H in-game, or from the main / pause menu (also shown on New Game) |

## New in this version
- **Ladders** - climb up to hidden ledges with crystals and potions.
- **Energy bar + Energy Potions** - blue flasks give +50 energy for your X bolt.
  Drink one at full energy and it heals a heart instead.
- **Different enemies in every world**
  | World | Enemies |
  |-------|---------|
  | 1 Temple | Walkers, Bats, Stone Hoppers, Thorn Spitter |
  | 2 Forest | Frogs (hoppers), Bats, Thorn Spitters, Walkers |
  | 3 Desert | Chargers, Spiked Crawlers, Bats, Cactus Spitters + Idris duel |
  | 4 Frozen | Frost Slimes, Frost Beasts, Ice Turrets, Bats, Spiked Crawlers + Rowan duel |
  | 5 Castle | Clockwork Sentinels (2 stomps), Time Wraiths (bolt only), Chargers, Spiked, Spitters, Bats + Timewyrm boss |
- Fixed: the exit portals in Levels 2-4 used to float past the end of the ground.
  All portals are now reachable.
- Note: Energy Bolts hurt regular enemies only. Rival princes and the Timewyrm
  still need stomps.

## Story & Characters
- **Aria** - a runaway princess turned warrior, unaware of the power she
  actually carries.
- **Caleb** - the guarded stranger (and secret prince) Aria keeps running
  into. Enemies-to-lovers energy at first; genuine partnership by the end.
- **Idris the Shade** (Level 3) and **Rowan of the Ice Court** (Level 4) -
  rival princes sent to stop Aria and Caleb. Each is defeated in a duel,
  not killed, and both turn up to help in the Level 5 finale.
- **The Hollow Sovereign** - the true villain, who seized Caleb's throne
  the moment he walked away from it and has been draining the World
  Dragon's crystal heart for power.
- **The Timewyrm** - the Sovereign's monster, fought at the climax of
  Level 5. It has 3 HP; stomp on top of it to damage it (same as regular
  enemies), but watch for its red "telegraph" flash just before it
  lunges - getting hit during a lunge costs 2 lives' worth of damage.

All character art (Aria, Caleb, the rival princes, the Hollow Sovereign,
the Timewyrm) is drawn procedurally in code with original designs - no
external image files are used or required.

## How to Run

1. Install Python 3.9+ (3.10–3.12 recommended).
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the game:
   ```
   python main.py
   ```

## Project Structure
See the original design spec — the project is split into `src/` (engine systems:
player, enemies, platforms, items, portals, dialogue, save system, menus, map),
`levels/` (one file per level layout), and `data/` (JSON save file + story dialogue).

## Notes
- All visuals are drawn procedurally with simple shapes/colors in Aria's violet,
  white, and gold color scheme — no external art files are required, so the game
  runs out of the box. Swap in real sprite images later by editing the `draw()`
  methods in `src/player.py`, `src/enemy.py`, etc., and loading images into the
  `assets/images/` folders (already scaffolded).
- Progress (current level, unlocked levels, completed levels, and total Time
  Crystals) is saved automatically to `data/save_game.json` every time you enter
  or complete a level, so "Continue Game" always resumes exactly where you left
  off — even mid-level.
