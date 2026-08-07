import argparse
import sys
from pathlib import Path
from pprint import pprint

from src.systems.config_parser import ConfigError, load_config


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Tester del parser de configuración "
        "para Pac-Man (42 Project)."
    )
    parser.add_argument(
        "config_file",
        nargs="?",
        default="src/systems/testingParser/example.json",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    config_path = Path(args.config_file)

    print(f"=== Probando parseo de configuración desde: '{config_path}' ===")

    try:
        config = load_config(config_path)
        print("\n✅ Configuración cargada y validada con éxito:")
        print("-" * 50)
        pprint(config, sort_dicts=False)
        print("-" * 50)
        print("Prueba completada correctamente.")
    except ConfigError as err:
        print(f"❌ [ERROR DE CONFIGURACIÓN] {err}", file=sys.stderr)
        sys.exit(1)
    except Exception as err:
        print(f"❌ [ERROR INESPERADO] {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
