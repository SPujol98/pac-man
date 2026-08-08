"""Script de pruebas para la clase App y la ventana de Pygame."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import App


def main():
    test_config = {
        "window": {"width": 1000, "height": 800, "fps": 80},
        "maze": {"width": 15, "height": 15, "seed": 100},
    }
    print("Lanzando App desde la suite de pruebas...")
    app = App(test_config)
    app.run()


if __name__ == "__main__":
    main()