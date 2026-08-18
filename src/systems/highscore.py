import json
from pathlib import Path
from typing import Any, Dict, List, Union


def _is_valid_entry(item: Any) -> bool:
    """Validates whether a raw highscore entry matches the required
    schema and constraints.
    Args:
        item: The object to validate, expected to be a dictionary.
    Returns:
        bool: True if the item is a dictionary containing a
        non-negative integer 'score' and an alphanumeric/space
        'name' string up to 10 characters long; False otherwise.
    """
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
    """Loads, validates, and sorts highscore entries from a JSON
    file in descending order.

    Reads the specified JSON file, filters out malformed or
    invalid records, and returns the remaining valid highscores
    sorted from highest to lowest score. If the file does not exist,
    an empty list is returned. If the file is corrupted, it is automatically
    deleted and an empty list is returned.

    Args:
        filepath: Path to the JSON highscores file.
        Defaults to "highscores.json".

    Returns:
        List[Dict[str, Any]]: A list of validated highscore
        dictionaries, each containing 'name' (str) and 'score'
        (int), ordered by score descending.
    """
    path = Path(filepath)
    if not path.is_file():
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                valid_entries = [
                    {
                        "name": item["name"].upper(),
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
    """Adds a new score, updates the scoreboard ranking,
    and persists it to a JSON file.

    Loads the current highscores, cleans up the provided player name,
    appends the new entry, sorts all entries in descending order,
    truncates the list to the top `max_entries`, and saves the result to disk.

    Args:
        name: The player's name. Whitespace is stripped,
        defaulting to "AAA" if empty.
        score: The numerical score achieved. Forced to be non-negative.
        filepath: Target JSON file path where highscores are stored.
        Defaults to "highscores.json".
        max_entries: Maximum number of leaderboard records to preserve.
        Defaults to 10.
    """
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
