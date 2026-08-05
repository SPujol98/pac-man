import json
from pathlib import Path
from typing import Any, Dict, List, Union


class ConfigError(Exception):
    """Custom exception for configuration errors."""
    pass


REQUIRED_KEYS = [
    "highscore_filename",
    "level",
    "lives",
    "pacgum",
    "points_per_pacgum",
    "points_per_super_pacgum",
    "points_per_ghost",
    "seed",
    "level_max_time",
]


def strip_comments(raw_text: str) -> str:
    clean_lines: List[str] = []
    for line in raw_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("#"):
            clean_lines.append(line)
    return "\n".join(clean_lines)


def _clamp_int(
    value: Any,
    min_val: int,
    max_val: Union[int, None] = None,
) -> int:
    """Convert to an integer and limit the value to a safe range."""
    val = int(value)
    if max_val is not None:
        return max(min_val, min(val, max_val))
    return max(min_val, val)


def validate_and_clamp_config(data: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(data, dict):
        raise ConfigError(
            "The root element of the JSON must be an object/dictionary."
            )

    missing = [key for key in REQUIRED_KEYS if key not in data]
    if missing:
        raise ConfigError(
            f"The following required keys are missing "
            f"from the JSON: {', '.join(missing)}"
        )

    validated: Dict[str, Any] = {}

    if (
        not isinstance(data["highscore_filename"], str)
        or not data["highscore_filename"].strip()
    ):
        raise ConfigError("'highscore_filename' must be a non-empty string.")
    validated["highscore_filename"] = data["highscore_filename"].strip()

    if not isinstance(data["level"], list) or len(data["level"]) == 0:
        raise ConfigError("'level' must be a non-empty list of levels.")

    validated_levels: List[Dict[str, Any]] = []
    for idx, lvl in enumerate(data["level"]):
        if not isinstance(lvl, dict):
            raise ConfigError(
                f"The level at position {idx} must be a JSON object."
                )
        if "width" not in lvl or "height" not in lvl:
            raise ConfigError(
                f"The level at position {idx} must "
                "include 'width' and 'height'."
            )
        try:
            w = _clamp_int(lvl["width"], min_val=5)
            h = _clamp_int(lvl["height"], min_val=5)
        except (ValueError, TypeError) as err:
            raise ConfigError(
                f"Invalid dimensions at this level {idx}: {err}"
            ) from err

        lvl_copy = lvl.copy()
        lvl_copy["width"] = w
        lvl_copy["height"] = h
        validated_levels.append(lvl_copy)

    validated["level"] = validated_levels

    try:
        validated["lives"] = _clamp_int(data["lives"], min_val=1, max_val=10)
        validated["pacgum"] = _clamp_int(data["pacgum"], min_val=0)
        validated["points_per_pacgum"] = _clamp_int(
            data["points_per_pacgum"],
            min_val=0,
        )
        validated["points_per_super_pacgum"] = _clamp_int(
            data["points_per_super_pacgum"],
            min_val=0
        )
        validated["points_per_ghost"] = _clamp_int(
            data["points_per_ghost"],
            min_val=0
        )
        validated["seed"] = _clamp_int(data["seed"], min_val=0)
        validated["level_max_time"] = _clamp_int(
            data["level_max_time"],
            min_val=10,
            max_val=3600,
        )
    except (ValueError, TypeError) as err:
        raise ConfigError(
            f"Invalid numeric value in the settings: {err}"
            ) from err

    for key, value in data.items():
        if key not in validated:
            validated[key] = value

    return validated


def load_config(filepath: Union[str, Path]) -> Dict[str, Any]:
    path = Path(filepath)
    if not path.is_file():
        raise ConfigError(f"Configuration file not found: '{filepath}'")

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw_content = f.read()
    except OSError as err:
        raise ConfigError(
            f"I/O error while reading '{filepath}': {err}"
            ) from err

    clean_content = strip_comments(raw_content)

    try:
        data = json.loads(clean_content)
    except json.JSONDecodeError as err:
        raise ConfigError(
            f"Invalid JSON format in '{filepath}': {err}"
            ) from err

    return validate_and_clamp_config(data)
