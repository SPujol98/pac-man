import json
from pathlib import Path
import re
from typing import Any, Dict, List, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    model_validator,
    field_validator
)


class ConfigError(Exception):
    """Custom exception for configuration errors."""
    pass


class LevelConfig(BaseModel):
    """Individual settings for each level of the game."""
    model_config = ConfigDict(extra="forbid")

    width: int = Field(ge=5, le=100)
    height: int = Field(ge=5, le=100)


class GameConfig(BaseModel):
    """Main game configuration diagram."""
    model_config = ConfigDict(extra="ignore")

    highscore_filename: str = Field(default="highscores.json", min_length=1)
    level: List[LevelConfig] = Field(
        default_factory=lambda: [LevelConfig(width=21, height=21)],
        min_length=1,)
    lives: int = Field(default=3, gt=0, le=8)
    pacgum: int = Field(default=42, gt=0, le=99999)
    points_per_pacgum: int = Field(default=10, ge=1, le=100)
    points_per_super_pacgum: int = Field(default=50, ge=2, le=1000)
    points_per_ghost: int = Field(default=200, ge=50, le=1000)
    seed: int = Field(default=42, gt=0)
    level_max_time: int = Field(default=90, ge=80, le=600)

    @model_validator(mode="before")
    @classmethod
    def check_missing_keys(cls, data: Any) -> Any:
        """Notify if any entries are missing from the dictionary "
        before applying the defaults."""
        if not isinstance(data, dict):
            return data

        required_keys = [
            "highscore_filename", "level", "lives", "pacgum",
            "points_per_pacgum", "points_per_super_pacgum",
            "points_per_ghost", "seed", "level_max_time"
        ]
        for key in required_keys:
            if key not in data:
                print(f"[Warning] Missing key '{key}'. "
                      "A safe default will be applied.")
        return data

    @field_validator("highscore_filename")
    @classmethod
    def validate_no_path_in_highscore(cls, v: str) -> str:
        path = Path(v)
        if "/" in v or "\\" in v or path.parent != Path("."):
            print(f"[Warning] 'highscore_filename' cannot be a path ({v}). "
                  "Defaulting to 'highscores.json'.")
            return "highscores.json"
        return v

    @field_validator("highscore_filename")
    @classmethod
    def validate_highscore_filename(cls, v: str) -> str:
        if "/" in v or "\\" in v or Path(v).parent != Path("."):
            print(
                f"[Warning] Invalid path in highscore filename '{v}'. "
                "Defaulting to 'highscores.json'."
            )
            return "highscores.json"

        if "." in v:
            if not v.endswith(".json"):
                print(
                    "[ERROR] The highscore file was corrupted or"
                    "invalid format. Defaulting to 'highscores.json'."
                )
                return "highscores.json"
            return v

        return f"{v}.json"


def strip_comments(text: str) -> str:
    """Strips '#', '//', and '/* ... */' comments from a string,
    preserving comment characters inside double-quoted string literals.
    """
    pattern = r'("(?:\\.|[^"\\])*")|/\*[\s\S]*?\*/|(?:#|//).*'

    def _replace(match: re.Match[str]) -> str:
        if match.group(1) is not None:
            return match.group(1)
        return ""

    return re.sub(pattern, _replace, text)


def load_config(filepath: Union[str, Path]) -> Dict[str, Any]:
    """Load the configuration in a fault-tolerant manner using self-healing."""
    path = Path(filepath)
    raw_json = {}

    if not path.is_file():
        print(f"[Warning] Configuration file '{filepath}' "
              "missing or not found. Safe defaults will be applied.")
    else:
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            cleaned_content = strip_comments(content)
            raw_json = json.loads(cleaned_content)
        except OSError as err:
            print(f"[Warning] I/O error while reading '{filepath}': "
                  f"{err}. Safe defaults will be applied.")
        except json.JSONDecodeError as err:
            print(f"[Warning] Invalid JSON format in '{filepath}': "
                  f"{err}. Safe defaults will be applied.")

    if not isinstance(raw_json, dict):
        print("[Warning] The root element must be a dictionary. "
              "Safe defaults will be applied.")
        return GameConfig.model_validate({}).model_dump()

    cleaned_json = dict(raw_json)

    try:
        config_obj = GameConfig.model_validate(cleaned_json)
        return config_obj.model_dump()

    except ValidationError as e:
        for error in e.errors():
            if error["loc"]:
                bad_key = str(error["loc"][0])
                if bad_key in cleaned_json:
                    msg = error.get("msg", "Invalid value")
                    print(f"[Warning] Invalid value for '{bad_key}': "
                          f"{msg}. Discarding key.")
                    del cleaned_json[bad_key]
        try:
            config_obj = GameConfig.model_validate(cleaned_json)
            return config_obj.model_dump()
        except ValidationError:
            print("[Error] Critical validation failure after cleanup. "
                  "Forcing safe defaults.")
            return GameConfig.model_validate({}).model_dump()
