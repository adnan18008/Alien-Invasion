import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCORE_FILE = ROOT / "scores.json"


def load_scores():
    """Return saved score records, or an empty list if none exist."""
    if not SCORE_FILE.exists():
        return []
    try:
        with SCORE_FILE.open(encoding="utf-8") as score_file:
            data = json.load(score_file)
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(data, list):
        return []
    records = []
    for item in data:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        score = item.get("score")
        if isinstance(name, str) and isinstance(score, int):
            records.append({"name": name, "score": score})
    return records


def save_score(name, score):
    """Append one player's result and write the full list back to JSON."""
    records = load_scores()
    records.append({"name": name, "score": int(score)})
    records.sort(key=lambda record: record["score"], reverse=True)
    with SCORE_FILE.open("w", encoding="utf-8") as score_file:
        json.dump(records, score_file, indent=2)
        score_file.write("\n")
    return records


class GameStats:
    """Track statistics for Alien Invasion."""

    def __init__(self, ai_game):
        """Initialize statistics."""
        self.settings = ai_game.settings
        self.records = load_scores()
        self.high_score = max((record["score"] for record in self.records), default=0)
        self.player_name = ""
        self.score_saved = False
        self.reset_stats()
        self.game_active = False

    def reset_stats(self):
        """Initialize statistics that can change during the game."""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1
        self.score_saved = False
