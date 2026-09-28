"""
story.py
--------
Loads intro/outro dialogue scenes for each level from data/story.json
and hands them to the DialogueBox system.
"""

import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import settings


def load_story():
    try:
        with open(settings.STORY_FILE, "r") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def get_intro(level_number):
    story = load_story()
    return story.get(str(level_number), {}).get("intro", [])


def get_outro(level_number):
    story = load_story()
    return story.get(str(level_number), {}).get("outro", [])


def get_boss_intro(level_number):
    story = load_story()
    return story.get(str(level_number), {}).get("boss_intro", [])


def get_boss_victory(level_number):
    story = load_story()
    return story.get(str(level_number), {}).get("boss_victory", [])


def get_rival_dialogue(level_number, rival_key, phase):
    """phase is 'intro' or 'victory'. Looks up story[level][f'{rival_key}_{phase}']."""
    story = load_story()
    return story.get(str(level_number), {}).get(f"{rival_key}_{phase}", [])
