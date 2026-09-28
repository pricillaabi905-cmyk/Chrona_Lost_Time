"""
save_system.py
---------------
Handles saving and loading the player's progress to/from a JSON file.

Save data format:
{
    "current_level": 5,
    "highest_unlocked_level": 5,
    "completed_levels": [1, 2, 3, 4],
    "time_crystals": 18
}

If the player reaches Level 5 (or any level) and quits or fails,
"current_level" is kept pointing at that level so "Continue Game"
resumes exactly there instead of restarting from Level 1.
"""

import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import settings


DEFAULT_SAVE = {
    "current_level": 1,
    "highest_unlocked_level": 1,
    "completed_levels": [],
    "time_crystals": 0,
}


def _ensure_data_dir():
    if not os.path.exists(settings.DATA_DIR):
        os.makedirs(settings.DATA_DIR)


def save_exists():
    return os.path.isfile(settings.SAVE_FILE)


def load_save():
    """Load save data from disk. Returns a fresh default save if none exists
    or the file is corrupted."""
    _ensure_data_dir()
    if not save_exists():
        return dict(DEFAULT_SAVE)
    try:
        with open(settings.SAVE_FILE, "r") as f:
            data = json.load(f)
        # Fill in any missing keys with defaults (keeps saves forward-compatible)
        for key, value in DEFAULT_SAVE.items():
            if key not in data:
                data[key] = value
        return data
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_SAVE)


def write_save(data):
    """Write the given save-data dictionary to disk."""
    _ensure_data_dir()
    with open(settings.SAVE_FILE, "w") as f:
        json.dump(data, f, indent=4)


def new_save():
    """Create and persist a brand-new save (used by 'New Game')."""
    data = dict(DEFAULT_SAVE)
    write_save(data)
    return data


def update_progress(data, level_number, completed=False, crystals_collected=0):
    """Update save data after playing a level.

    - Always updates 'current_level' so the game can resume where the
      player left off, even if they quit mid-level or lost.
    - If 'completed' is True, marks the level as completed and unlocks
      the next one.
    """
    data["current_level"] = level_number
    data["time_crystals"] = data.get("time_crystals", 0) + crystals_collected

    if completed:
        if level_number not in data["completed_levels"]:
            data["completed_levels"].append(level_number)
            data["completed_levels"].sort()
        next_level = level_number + 1
        if next_level > data.get("highest_unlocked_level", 1):
            data["highest_unlocked_level"] = min(next_level, settings.TOTAL_LEVELS)
        # After finishing a level, move current_level forward so Continue
        # naturally resumes at the next unlocked level.
        if next_level <= settings.TOTAL_LEVELS:
            data["current_level"] = next_level

    write_save(data)
    return data
