import json
from pathlib import Path
from typing import Any, Dict, List, Union


def load_highscores(
        filepath: Union[str, Path] = "highscores.json"
        ) -> List[Dict[str, Any]]:
    """Load and sort the top scores from a JSON file."""
    path = Path(filepath)
    if not path.is_file():
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                valid_entries = [
                    {
                        "name": str(item.get("name", "AAA"))[:10],
                        "score": max(0, int(item.get("score", 0))),
                    }
                    for item in data
                    if isinstance(item, dict)
                ]
                return sorted(valid_entries,
                              key=lambda x: x["score"],
                              reverse=True)
    except Exception as err:
        print(f"[Warning] Could not load highscores from '{filepath}': {err}")

    return []


def save_highscore(
    name: str,
    score: int,
    filepath: Union[str, Path] = "highscores.json",
    max_entries: int = 10,
) -> None:
    """Add a new score and keep only the top N scores."""
    scores = load_highscores(filepath)
    clean_name = name.strip().upper() or "AAA"

    scores.append({"name": clean_name, "score": max(0, int(score))})
    scores = sorted(scores,
                    key=lambda x: x["score"],
                    reverse=True)[:max_entries]

    path = Path(filepath)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=4)
        print(f"[Info] Highscore saved: {clean_name} - {score}")
    except Exception as err:
        print(f"[Error] Failed to save highscores: {err}")
