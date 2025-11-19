"""Utility to load settings.json for commands and chat configs."""

import json

def load_settings(path="settings.json"):
    with open(path, "r", encoding="utf8") as f:
        return json.load(f)
