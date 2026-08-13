import json
import sys
from pathlib import Path
from typing import Any, cast
from src.app import App

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def load_config() -> dict[str, Any]:
    """Carga el archivo config.json dinámicamente desde
    la raíz del proyecto."""

    possible_paths = [
        PROJECT_ROOT / "config.json",
        Path("config.json"),
        Path(__file__).parent / "config.json"
    ]

    for config_path in possible_paths:
        if config_path.is_file():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    print("Cargando configuración desde: "
                          f"{config_path.resolve()}")
                    return cast(dict[str, Any], json.load(f))
            except Exception as err:
                print(f"[Error] No se pudo leer {config_path}: {err}")

    print("[Info] No se encontró config.json, "
          "usando configuración de respaldo...")
    return {
        "window": {"width": 800, "height": 600, "fps": 60},
        "lives": 4,
        "points_per_pacgum": 10,
        "points_per_super_pacgum": 50,
        "seed": 42,
        "level_max_time": 80,
        "level": [
            {"width": 21, "height": 21}
        ]
    }


def main() -> None:
    config = load_config()

    print("Lanzando App desde la suite de pruebas...")
    app = App(config)
    app.run()


if __name__ == "__main__":
    main()
