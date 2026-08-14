import sys
from src.app import App
import argparse
from src.systems.config_parser import load_config

'''
def main() -> None:

    parser = argparse.ArgumentParser(description="pacman")

    parser.add_argument('config_path',
                        nargs='?',
                        default='config.json',
                        )

    args = parser.parse_args()

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
'''


def main() -> None:

    parser = argparse.ArgumentParser(description="pacman")

    parser.add_argument('config_path',
                        nargs='?',
                        default='config.json',
                        )

    args = parser.parse_args()

    config = load_config(args.config_path)
    print("Starting Pac-Man 42...")
    app = App(config)
    app.run()


def _safe_pygame_quit() -> None:
    """Safely close Pygame contexts if initialized."""
    try:
        import pygame
        pygame.quit()
    except Exception:
        pass


if __name__ == "__main__":
    main()
