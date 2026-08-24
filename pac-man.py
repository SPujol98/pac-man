import argparse
import os
import signal
import sys
from typing import Any

from src.app import App
from src.systems.config_parser import load_config


def handle_sigquit(signum: int, frame: Any) -> None:
    """Exit gracefully on Ctrl+\\ (SIGQUIT)."""
    print("\n[Info] Game interrupted by user (Ctrl+\\). "
          "Exiting gracefully...")
    _safe_pygame_quit()
    sys.exit(0)


def get_resource_path(relative_path: str) -> str:
    """Resolve a resource path in development and PyInstaller builds."""
    if hasattr(sys, '_MEIPASS'):
        bundled_path = os.path.join(sys._MEIPASS, relative_path)
        if os.path.exists(bundled_path):
            return bundled_path
    return relative_path


def main() -> None:
    """Entry point: validate the config argument and launch the app."""
    if hasattr(signal, 'SIGQUIT'):
        signal.signal(signal.SIGQUIT, handle_sigquit)
    parser = argparse.ArgumentParser(description="Pac-Man 42")

    parser.add_argument(
        'config_path',
        nargs='?',
        default='config.json',
        help='Path to the JSON configuration file (default: config.json)'
    )
    args = parser.parse_args()

    config_file = get_resource_path(args.config_path)

    if not config_file.lower().endswith('.json'):
        print(
            f"Error: Invalid file '{args.config_path}'. "
            "Must be a .json file.",
            file=sys.stderr)
        sys.exit(1)

    try:
        config = load_config(config_file)
        print("Starting Pac-Man 42...")
        app = App(config)
        app.run()

    except Exception as e:
        print(f"Error during execution: {e}", file=sys.stderr)
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n[Info] Game interrupted by user (Ctrl+C). "
              "Exiting gracefully...")
        _safe_pygame_quit()


def _safe_pygame_quit() -> None:
    """Safely close Pygame contexts if initialized."""
    try:
        import pygame
        pygame.quit()
    except Exception:
        pass


if __name__ == "__main__":
    main()
