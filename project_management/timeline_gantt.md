# Timeline & Gantt — Planned vs. Actual Progress

| Phase | Planned Tasks | Scheduled | Actual | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 0: Foundations** | Definition of `states.py`, folder structure, Makefile, `pyproject.toml`, and `.gitignore`. | Day 1 | Day 1 | Completed |
| **Phase 1: Minimum Verticals** | Hybrid movement (`Player` + `entity`)[cite: 1], configuration parser (`config_parser.py`), and maze loader (`maze_loader.py`). | Days 2 - 3 | Days 2 - 3 | Completed |
| **Phase 2: Core Gameplay** | `Game` state, collisions, ghost AI (`ghost.py`), pixel renderer (`renderer.py`), and main loop (`app.py`). | Days 4 - 6 | Days 4 - 7 | Completed (+1d AI tuning) |
| **Phase 3: Systems** | Frightened/Eaten mode, level progression (`progression.py`), cheat mode (`cheat_mode.py`), HUD, menus (`menus/...`), and highscore system (`highscore.py`). | Days 7 - 9 | Days 8 - 10 | Completed |
| **Phase 4: Polish & Delivery** | Tests (`tests/`), packaging script (`build.py`), documentation, `make lint` check, and deployment to a public platform. | Days 10 - 11 | Days 11 - 12 | Completed |