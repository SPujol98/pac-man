import json
from pathlib import Path
from typing import Any, Dict, List, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    ValidationInfo,
    field_validator,
    model_validator,
)


class ConfigError(Exception):
    """Custom exception for configuration errors."""
    pass


class LevelConfig(BaseModel):
    """Individual settings for each level of the game."""
    model_config = ConfigDict(extra="ignore")

    width: int = Field(default=21)
    height: int = Field(default=21)

    @field_validator("width", "height", mode="before")
    @classmethod
    def clamp_dimension(cls, v: Any, info: ValidationInfo) -> int:
        safe_default = 21
        if isinstance(v, bool):
            print(f"[Warning] Boolean not allowed for '{info.field_name}'. "
                  f"Using default: {safe_default}")
            return safe_default
        try:
            return max(5, int(v))
        except (ValueError, TypeError):
            print(f"[Warning] Invalid value for '{info.field_name}'. "
                  f"Using default: {safe_default}")
            return safe_default


class GameConfig(BaseModel):
    """Main game configuration diagram."""
    model_config = ConfigDict(extra="ignore")

    highscore_filename: str = Field(default="highscores.json")
    level: List[LevelConfig] = Field(default_factory=lambda: [LevelConfig()])
    lives: int = Field(default=3, gt=0, le=8)
    pacgum: int = Field(default=42)
    points_per_pacgum: int = Field(default=10, gt=0, le=100)
    points_per_super_pacgum: int = Field(default=50, gt=1, le=1000)
    points_per_ghost: int = Field(default=200, gt=50, le=1000)
    seed: int = Field(default=42, gt=0)
    level_max_time: int = Field(default=90, ge=80, le=600)

    @model_validator(mode="before")
    @classmethod
    def check_missing_keys(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            print("[Warning] The root element must be a dictionary. "
                  "Safe defaults will be applied.")
            return {}

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

    @field_validator("highscore_filename", mode="before")
    @classmethod
    def validate_filename(cls, v: Any) -> str:
        safe_default = "highscores.json"
        if not isinstance(v, str) or not v.strip():
            print(f"[Warning] 'highscore_filename' is invalid/empty. "
                  f"Using default: '{safe_default}'")
            return safe_default
        return v.strip()

    @field_validator("level", mode="before")
    @classmethod
    def validate_level(cls, v: Any) -> List[Any]:
        if not isinstance(v, list) or len(v) == 0:
            print("[Warning] 'level' must be a non-empty list. "
                  "Using a default level.")
            return [{"width": 21, "height": 21}]
        return v

    @field_validator("lives", mode="before")
    @classmethod
    def clamp_lives(cls, v: Any) -> int:
        safe_default = 3
        if isinstance(v, bool):
            print(f"[Warning] Boolean not allowed for 'lives'. "
                  f"Using default: {safe_default}")
            return safe_default
        try:
            return max(1, min(int(v), 10))
        except (ValueError, TypeError):
            print(f"[Warning] Invalid value for 'lives'. "
                  f"Using default: {safe_default}")
            return safe_default

    @field_validator(
        "pacgum", "points_per_pacgum", "points_per_super_pacgum",
        "points_per_ghost", "seed", mode="before"
    )
    @classmethod
    def clamp_non_negative(cls, v: Any, info: ValidationInfo) -> int:
        defaults = {
            "pacgum": 42, "points_per_pacgum": 10,
            "points_per_super_pacgum": 50, "points_per_ghost": 200, "seed": 42
        }
        field_name = info.field_name or ""
        safe_default = defaults.get(field_name, 0)

        if isinstance(v, bool):
            print(f"[Warning] Boolean not allowed for '{field_name}'. "
                  f"Using default: {safe_default}")
            return safe_default
        try:
            return max(0, int(v))
        except (ValueError, TypeError):
            print(f"[Warning] Invalid numeric value for '{field_name}'. "
                  f"Using default: {safe_default}")
            return safe_default

    @field_validator("level_max_time", mode="before")
    @classmethod
    def clamp_max_time(cls, v: Any) -> int:
        safe_default = 90
        if isinstance(v, bool):
            print(f"[Warning] Boolean not allowed for 'level_max_time'. "
                  f"Using default: {safe_default}")
            return safe_default
        try:
            return max(10, min(int(v), 3600))
        except (ValueError, TypeError):
            print(f"[Warning] Invalid value for 'level_max_time'. "
                  f"Using default: {safe_default}")
            return safe_default


def load_config(filepath: Union[str, Path]) -> Dict[str, Any]:
    """Fail-safe configuration loading. Never throws exceptions."""
    path = Path(filepath)
    raw_json = {}

    if not path.is_file():
        print(f"[Warning] Configuration file '{filepath}' "
              "missing or not found. Safe defaults will be applied.")
    else:
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw_json = json.load(f)
        except OSError as err:
            print(f"[Warning] I/O error while reading '{filepath}': {err}. "
                  "Safe defaults will be applied.")
        except json.JSONDecodeError as err:
            print(f"[Warning] Invalid JSON format in '{filepath}': {err}. "
                  "Safe defaults will be applied.")

    try:
        config_obj = GameConfig.model_validate(raw_json)
        return config_obj.model_dump()
    except ValidationError:
        print("[Error] Critical validation failure. Forcing safe defaults.")
        return GameConfig.model_validate({}).model_dump()
