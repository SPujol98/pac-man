import argparse
import sys
from src.app import App
from src.systems.config_parser import load_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Pac-Man 42")

    parser.add_argument(
        'config_path',
        help='Path to the JSON configuration file'
    )
    args = parser.parse_args()
    if not args.config_path.lower().endswith('.json'):
        print(
            f"Error: Invalid file '{args.config_path}'. "
            "Must be a .json file.",
            file=sys.stderr)
        sys.exit(1)

    try:
        config = load_config(args.config_path)
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
