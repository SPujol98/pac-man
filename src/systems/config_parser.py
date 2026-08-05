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
        """Apply a clamp to the map dimensions (minimum 5)."""
        safe_default = 21
        if isinstance(v, bool):
            print(
                f"[Warning] A Boolean value is not allowed "
                f"for '{info.field_name}'. Using default: {safe_default}"
            )
            return safe_default
        try:
            return max(5, int(v))
        except (ValueError, TypeError):
            print(
                f"[Warning] Invalid value for '{info.field_name}'. "
                f"Using default: {safe_default}"
            )
            return safe_default


class GameConfig(BaseModel):
    """Main game configuration diagram."""

    model_config = ConfigDict(extra="ignore")

    highscore_filename: str = Field(default="highscores.json")
    level: List[LevelConfig] = Field(default_factory=lambda: [LevelConfig()])
    lives: int = Field(default=3)
    pacgum: int = Field(default=42)
    points_per_pacgum: int = Field(default=10)
    points_per_super_pacgum: int = Field(default=50)
    points_per_ghost: int = Field(default=200)
    seed: int = Field(default=42)
    level_max_time: int = Field(default=90)

    @model_validator(mode="before")
    @classmethod
    def check_missing_keys(cls, data: Any) -> Any:
        """Logs a warning for any missing required key before validation."""
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
        """Validate that the highscore filename is not empty."""
        safe_default = "highscores.json"
        if not isinstance(v, str):
            print("[Warning] 'highscore_filename' must be a string. "
                  f"Using default: '{safe_default}'")
            return safe_default

        stripped = v.strip()
        if not stripped:
            print("[Warning] 'highscore_filename' cannot be empty. "
                  f"Using default: '{safe_default}'")
            return safe_default
        return stripped

    @field_validator("level", mode="before")
    @classmethod
    def validate_level(cls, v: Any) -> List[Any]:
        """Ensure level is a non-empty list."""
        if not isinstance(v, list) or len(v) == 0:
            print("[Warning] 'level' must be a non-empty list. "
                  "Using a default level.")
            return [{"width": 21, "height": 21}]
        return v

    @field_validator("lives", mode="before")
    @classmethod
    def clamp_lives(cls, v: Any) -> int:
        """Apply a clamp to the wires numbered 1 through 10."""
        safe_default = 3
        if isinstance(v, bool):
            print(f"[Warning] A Boolean value is not allowed for 'lives'. "
                  f"Using default: {safe_default}")
            return safe_default
        try:
            return max(1, min(int(v), 10))
        except (ValueError, TypeError):
            print(f"[Warning] Invalid value for 'lives'. "
                  f"Using default: {safe_default}")
            return safe_default

    @field_validator(
        "pacgum",
        "points_per_pacgum",
        "points_per_super_pacgum",
        "points_per_ghost",
        "seed",
        mode="before",
    )
    @classmethod
    def clamp_non_negative(cls, v: Any, info: ValidationInfo) -> int:
        """Ensures that numerical values are not negative."""
        defaults = {
            "pacgum": 42,
            "points_per_pacgum": 10,
            "points_per_super_pacgum": 50,
            "points_per_ghost": 200,
            "seed": 42
        }
        safe_default = defaults.get(info.field_name, 0)

        if isinstance(v, bool):
            print(f"[Warning] Boolean values are not allowed "
                  f"for '{info.field_name}'. Using default: {safe_default}")
            return safe_default
        try:
            return max(0, int(v))
        except (ValueError, TypeError):
            print(f"[Warning] Invalid numeric value for '{info.field_name}'. "
                  f"Using default: {safe_default}")
            return safe_default

    @field_validator("level_max_time", mode="before")
    @classmethod
    def clamp_max_time(cls, v: Any) -> int:
        """Set the clamp time to a value between 10 and 3,600 seconds."""
        safe_default = 90
        if isinstance(v, bool):
            print("[Warning] A Boolean value is not allowed for "
                  f"'level_max_time'. Using default: {safe_default}")
            return safe_default
        try:
            return max(10, min(int(v), 3600))
        except (ValueError, TypeError):
            print("[Warning] Invalid value for 'level_max_time'. "
                  f"Using default: {safe_default}")
            return safe_default


def strip_comments(raw_text: str) -> str:
    """Removes in-line and full-line comments starting with '#'."""
    clean_lines: List[str] = []
    for line in raw_text.splitlines():
        code_part = line.split("#")[0]
        if code_part.strip():
            clean_lines.append(code_part)
        else:
            clean_lines.append("")
    return "\n".join(clean_lines)


def load_config(filepath: Union[str, Path]) -> Dict[str, Any]:
    """Carga de configuración a prueba de fallos. Nunca lanza excepciones."""
    path = Path(filepath)
    raw_json = {}

    if not path.is_file():
        print(f"[Warning] Configuration file not found: '{filepath}'. "
              "Safe defaults will be applied.")
    else:
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw_content = f.read()
            clean_content = strip_comments(raw_content)
            raw_json = json.loads(clean_content)
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
