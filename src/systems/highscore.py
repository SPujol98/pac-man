import json
from pathlib import Path
from typing import Any, Dict, List, Union


def _is_valid_entry(item: Any) -> bool:
    if not isinstance(item, dict):
        return False
    score = item.get("score")
    name = item.get("name")
    if not isinstance(score, int) or not isinstance(name, str):
        return False
    if (score < 0 or len(name) > 10 or not
            all(char.isalnum() or char == " " for char in name)):
        return False
    return True


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
                        "name": item["name"],
                        "score": item["score"],
                    }
                    for item in data if _is_valid_entry(item)
                ]
                return sorted(valid_entries,
                              key=lambda x: x["score"],
                              reverse=True)
    except Exception as err:
        print(f"[Warning] Could not load highscores from '{filepath}': {err}")
        Path(path).unlink()
        print("The corrupt file has been removed.")
    return []


def save_highscore(
    name: str,
    score: int,
    filepath: Union[str, Path] = "highscores.json",
    max_entries: int = 10,
) -> None:
    """Add a new score and keep only the top N scores."""
    scores = load_highscores(filepath)
    clean_name = name.strip() or "AAA"

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
