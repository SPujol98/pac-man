import json
from pathlib import Path
from typing import Any, Dict, List, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
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
    def clamp_dimension(cls, v: Any) -> int:
        """Apply a clamp to the map dimensions (minimum 5)."""
        try:
            return max(5, int(v))
        except (ValueError, TypeError) as err:
            raise ValueError(f"Invalid level dimension: {v}") from err


class GameConfig(BaseModel):
    """Main game configuration diagram."""

    model_config = ConfigDict(extra="ignore")

    highscore_filename: str
    level: List[LevelConfig] = Field(min_length=1)
    lives: int
    pacgum: int
    points_per_pacgum: int
    points_per_super_pacgum: int
    points_per_ghost: int
    seed: int
    level_max_time: int

    @field_validator("highscore_filename", mode="after")
    @classmethod
    def validate_filename(cls, v: str) -> str:
        """Validate that the highscore filename is not empty."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("'highscore_filename' cannot be empty.")
        return stripped

    @field_validator("lives", mode="before")
    @classmethod
    def clamp_lives(cls, v: Any) -> int:
        """Apply a clamp to the wires numbered 1 through 10."""
        return max(1, min(int(v), 10))

    @field_validator(
        "pacgum",
        "points_per_pacgum",
        "points_per_super_pacgum",
        "points_per_ghost",
        "seed",
        mode="before",
    )
    @classmethod
    def clamp_non_negative(cls, v: Any) -> int:
        """Ensures that numerical values are not negative."""
        return max(0, int(v))

    @field_validator("level_max_time", mode="before")
    @classmethod
    def clamp_max_time(cls, v: Any) -> int:
        """Set the clamp time to a value between 10 and 3,600 seconds."""
        return max(10, min(int(v), 3600))


def strip_comments(raw_text: str) -> str:

    clean_lines: List[str] = []
    for line in raw_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("#"):
            clean_lines.append(line)
    return "\n".join(clean_lines)


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
        raw_json = json.loads(clean_content)
        config_obj = GameConfig.model_validate(raw_json)
        return config_obj.model_dump()
    except json.JSONDecodeError as err:
        raise ConfigError(
            f"Invalid JSON format in '{filepath}': {err}"
            ) from err
    except ValidationError as err:
        raise ConfigError(
            f"Validation error in the configuration: {err}"
            ) from err
