# Team Structure & Role Division

| Team Member | Primary Role | Assigned Components & Files |
| :--- | :--- | :--- |
| **Programmer A** | Engine & Simulation (Core Logic) | `src/core/` (`game.py`, `level.py`, `progression.py`)<br>`src/entities/` (`entity.py`, `player.py`, `ghost.py`, `collectibles.py`)<br>`src/systems/cheat_mode.py`<br>`tests/test_progression.py` |
| **Programmer B** | UI, Systems & Data (Presentation Layer) | `pac-man.py`, `src/app.py`<br>`src/level_manager/maze_loader.py`<br>`src/ui/` (`renderer.py`, `play_screen.py`, `hud.py`, `input_handler.py`),<br>`src/ui/menus` (`base_score_entry.py`, `base_screen.py`, `end_screens.py`, `highscores_menu.py`, `instructions_menu.py`, `main_menu.py`, `pause_menu.py`)<br>`src/systems/` (`config_parser.py`, `highscore.py`)<br>`packaging/build.py`|
| **Shared / Both** | Architecture & Infrastructure | `src/states.py`, `Makefile`, `README.md`, `project_management/` |