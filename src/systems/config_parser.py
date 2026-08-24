import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Union

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


class WindowConfig(BaseModel):
    """Optional window settings; None means auto-fit to the desktop."""
    model_config = ConfigDict(extra="ignore")

    width: Optional[int] = Field(default=None, ge=400, le=7680)
    height: Optional[int] = Field(default=None, ge=300, le=4320)
    fps: Optional[int] = Field(default=None, ge=30, le=360)


class LevelConfig(BaseModel):
    """Validated width/height settings for a single level."""
    model_config = ConfigDict(extra="forbid")

    width: int = Field(ge=5, le=45)
    height: int = Field(ge=5, le=45)


class GameConfig(BaseModel):
    """Main game configuration schema with safe defaults."""
    model_config = ConfigDict(extra="ignore")

    highscore_filename: str = Field(default="highscores.json", min_length=1)
    window: WindowConfig = Field(default_factory=WindowConfig)
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
        """Warn about any missing keys before defaults are applied."""
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

    @field_validator("level", mode="before")
    @classmethod
    def filter_valid_levels(cls, levels: Any) -> Any:
        """Discard invalid level entries instead of failing the whole file."""
        if not isinstance(levels, list):
            return levels
        valid_levels = []
        for item in levels:
            try:

                valid_levels.append(LevelConfig.model_validate(item))
            except ValidationError:
                print(f"[Warning] Discarding invalid level entry: {item}")
        return valid_levels if valid_levels else None

    @field_validator("highscore_filename")
    @classmethod
    def validate_highscore_filename(cls, v: str) -> str:
        """Reject unsafe or non-JSON filenames, falling back to the default."""
        v = v.strip()
        FORBIDDEN_CHARS = set(r'/\:*?"<>|' + "\n\r\t\0")
        has_invalid_chars = any(c in FORBIDDEN_CHARS for c in v) or any(
            ord(c) < 32 for c in v
        )
        is_directory_path = Path(v).name != v or Path(v).parent != Path(".")
        if has_invalid_chars or is_directory_path:
            print(
                f"[Warning] Invalid highscore filename {repr(v)}. "
                "Defaulting to 'highscores.json'."
            )
            return "highscores.json"

        if "." in v:
            if not v.endswith(".json"):
                print(
                    "[ERROR] The highscore file was corrupted or"
                    " invalid format. Defaulting to 'highscores.json'."
                )
                return "highscores.json"
            return v
        return f"{v}.json"


def strip_comments(text: str) -> str:
    """Strip '#', '//', and '/* ... */' comments outside string literals."""
    pattern = r'("(?:\\.|[^"\\])*")|/\*[\s\S]*?\*/|(?:#|//).*'

    def _replace(match: re.Match[str]) -> str:
        if match.group(1) is not None:
            return match.group(1)
        return ""

    return re.sub(pattern, _replace, text)


def load_config(filepath: Union[str, Path]) -> Dict[str, Any]:
    """Load the config self-healingly: clamp bad values to safe defaults."""
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
