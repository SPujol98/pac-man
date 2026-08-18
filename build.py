import os
import shutil
import subprocess
import sys


def build_game():
    print("=== Pac-Man 42 Build Script ===")

    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

    dist_dir = "dist"
    build_dir = "build"

    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)

    sep = ";" if sys.platform.startswith("win") else ":"

    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name=PacMan42",
        f"--add-data=src{sep}src",
        f"--add-data=assets{sep}assets",
        f"--add-data=INSTRUCTIONS.txt{sep}.",
        "pac-man.py"
    ]

    print("Running PyInstaller...")
    subprocess.run(cmd, check=True)

    target_folder = os.path.join("dist", "PacMan42")
    if os.path.exists("config.json"):
        shutil.copy("config.json", os.path.join(target_folder, "config.json"))

    print(f"\n[SUCCESS] Game successfully packaged in: {target_folder}")


if __name__ == "__main__":
    build_game()