*This project has been created as part of the 42 curriculum by spujol-s, sasanche.*

# 🟡 Pac-Man

![Language](https://img.shields.io/badge/Language-Python-blue)
![Engine](https://img.shields.io/badge/Engine-Pygame-green)
![Typing](https://img.shields.io/badge/mypy-strict-informational)

---

## Description

A from-scratch clone of the 1980 arcade Pac-Man, built as a two-person project around a strict MVC split: one person owns everything that happens in the game world (movement rules, collisions, ghost AI, level progression), the other owns everything about how it's shown and stored (rendering, menus, config parsing, highscores). The only thing shared between the two sides is a fixed entity contract, agreed on day one, so both halves got built in parallel without stepping on each other.

The game loop runs on delta time rather than fixed ticks, movement uses a hybrid pixel/grid model (entities move continuously in pixels but only decide where to turn once aligned to a grid cell), and mazes come from the external `A-Maze-ing` package instead of hand-authored maps. There are 10+ levels — level 1 uses a fixed seed for reproducible testing, the rest are randomized.

---

## Instructions

### Requirements

- Python 3.10+
- [`uv`](https://github.com/astral-sh/uv)
- Pygame (installed automatically via `uv sync`)

### Install

```bash
make install
```

Runs `uv sync` to install project dependencies, then installs the assigned maze generator (`mazegenerator-00001-py3-none-any.whl`) as a local wheel — it's not published on PyPI, so `UV_SKIP_WHEEL_FILENAME_CHECK=1` is needed to get `uv pip install` to accept a non-standard wheel filename.

### Run

```bash
make run
```

or directly:

```bash
uv run python3 pac-man.py config.json
```

`pac-man.py` expects exactly one argument: the path to a `.json` config file. Anything else (missing file, wrong extension, malformed argument) is handled without a traceback.

### Debug

```bash
make debug
```

Runs the game under `pdb` (`uv run python3 -m pdb pac-man.py`).

### Test

```bash
make test
```

Runs `uv run python -m pytest -v -s -o pythonpath=. tests/`. Not graded, but kept as a sanity check during development — this suite is still being built out.

### Lint

```bash
make lint         # flake8 + mypy (--warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs)
make lint-strict  # flake8 + mypy --strict
```

Both exclude `.venv` from the mypy check.

### Clean

```bash
make clean
```

Removes `__pycache__`, `.mypy_cache`, `.pytest_cache`, `*.egg-info`, and `.venv`.

---

## Configuration

The game reads a `config.json` at startup. Comments are allowed even though this isn't strictly valid JSON: any line starting with `#` is stripped before the file is handed to `json.loads`.

Example:

```json
{
    "highscore_filename": "highscores.json",
    "lives": 3,
    "pacgum": 42,
    "points_per_pacgum": 10,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 200,
    "seed": 42,
    "level_max_time": 100,
    "level": [
        {
            "width": 15,
            "height": 15
        }
    ]
}
```

| Key | Meaning | Default behavior if missing/invalid |
|---|---|---|
| `highscore_filename` | File used to persist the Top 10 | Falls back to a hardcoded default filename |
| `lives` | Starting player lives | Falls back to `3` |
| `pacgum` | Number of regular pacgums placed per level | Falls back to a hardcoded default |
| `points_per_pacgum` | Score awarded per regular pacgum | Falls back to `10` |
| `points_per_super_pacgum` | Score awarded per super-pacgum | Falls back to `50` |
| `points_per_ghost` | Score awarded per ghost eaten while frightened | Falls back to `200` |
| `seed` | Seed used for level 1's maze | Falls back to `42`; levels 2+ always use a randomized seed regardless of this value |
| `level_max_time` | Time limit (seconds) per level | Falls back to a hardcoded default |
| `level` | Width/height of the maze grid | Falls back to hardcoded dimensions |

The parser follows a zero-trust approach: invalid types (a string where an int is expected, a negative value where only non-negative makes sense) are clamped to sane bounds rather than raising, unknown keys are ignored, and missing keys silently fall back to hardcoded defaults. There is no path through a malformed config that produces a traceback.

---

## Highscore

Scores are persisted as a Top 10 list in a JSON file (`highscore_filename` in the config, `highscores.json` by default). Every entry is validated on load through a single guard function that checks two things: the score is a non-negative integer, and the name is 1–10 alphanumeric characters or spaces.

The system was built to survive manual tampering rather than just honest gameplay: if the file has been hand-edited into something invalid, or `json.load` fails outright, the loader doesn't try to salvage or partially repair it — it deletes the corrupted file and returns an empty list, so the game keeps running instead of crashing on a highscore screen. This trades "recover what we can" for "never crash," which given the project's zero-traceback requirement was the right side of that trade-off.

---

## Maze Generation

Mazes are generated through the external `A-Maze-ing` package assigned by another group, distributed as a prebuilt wheel (`mazegenerator-00001-py3-none-any.whl`) rather than as source — it's installed as-is via `uv pip install` and never modified. `src/level_manager/maze_loader.py` adapts to whatever interface that package exposes, not the other way around. The loader forces `PERFECT=False`, since a perfect maze — exactly one path between any two cells — doesn't leave room for the loops and alternate routes that make ghost-chasing and escaping meaningful in Pac-Man.

Level 1 always uses a fixed seed (`42` by default, configurable) so the first level is reproducible for testing and defense. Levels 2 and onward use randomized seeds, so no two playthroughs past the first level look the same.

---

## Implementation

### Movement: hybrid grid/pixel model

Entities track a logical cell `(col, row)` for decision-making and a pixel position `(px, py)` for rendering. They move continuously in pixels, interpolating toward the center of the next cell, and only evaluate navigation decisions — turning, colliding, eating a pacgum, a ghost choosing a direction — once they're aligned to a cell center. This keeps all the actually hard logic (collisions, AI) reasoning over a small discrete grid instead of continuous coordinates, while the screen still shows smooth per-pixel motion.

Player turns are buffered: pressing a direction before reaching the next intersection queues that turn, which gets applied automatically once it becomes valid. This is what makes the controls feel responsive rather than requiring frame-perfect input, matching the feel of the original arcade cabinet.

### Time: delta-time driven, not tick-based

```python
dt = clock.tick(60) / 1000.0
dt = min(dt, 0.05)
game.update(dt)
```

Every entity moves at `speed * dt`, so gameplay speed is independent of frame rate. All timers — the per-level countdown, frightened mode duration, ghost respawn delay — accumulate `dt` rather than counting frames. The clamp on `dt` is not optional: without it, a lag spike or a dragged window produces one oversized `dt` that can tunnel an entity straight through a wall.

### Ghost AI

Ghosts run a finite state machine with four states: `CHASE`, `SCATTER`, `FRIGHTENED`, and `EATEN`. Like the player, they only make navigation decisions at cell-aligned intersections.

The four ghosts share a global wave timer rather than deciding chase/scatter independently: the game starts in `SCATTER` for 7 seconds, then flips to `CHASE` for 15, then back to `SCATTER`, alternating for as long as the level runs. Any ghost currently `FRIGHTENED` or `EATEN` is left alone when the wave flips — it only picks up the new global state once it's back to normal. Eating a super-pacgum interrupts the wave: every non-eaten ghost switches to `FRIGHTENED` for 8 seconds, counted down independently of the wave timer, and reverts to whatever the global state was when the frightened window ends. When eaten, a ghost doesn't return to a shared central house — it heads back to its own corner spawn point.

Losing a life resets more than just the player: `Game._update()` also resets every ghost's state and position back to its spawn corner, so each life starts clean rather than mid-chase.

### Cheat mode

There's no separate cheat module — cheat behavior is a handful of flags checked directly where they matter. `Player` carries an `is_invincible` flag that short-circuits the life-loss branch in `Game._update()`: a ghost colliding with the player is a normal FSM transition either way, but the life is only spent if the flag is off. The rest of the cheat set (level skip, ghost freeze, extra lives) follows the same pattern — a state check inline in `Game` or `Player` rather than a dedicated system, kept deliberately simple since the whole point is helping a reviewer test features fast, not building a second control layer.

### UI Architecture & Programmer B Overview

Base Screen & Polymorphism (base_screen.py): An abstract BaseScreen class enforces standard methods (handle_input(), update(), draw()). All screens inherit from it, enabling the main game loop to update and render active screens polymorphically.

Menu Hierarchy (menus/): Manages user navigation across the Main Menu, Pause Menu, Instructions, High Scores, and End Screens (Game Over/Victory with score entry inheritance).

In-Game Interface & Rendering:
    
* play_screen.py: Coordinates active gameplay state, combining the map, entities, and UI overlay.
* hud.py: Displays real-time game telemetry (score, remaining lives, timer, and level).
* renderer.py: Encapsulates drawing primitives to decouple graphic calls from core logic.
* input_handler.py: Centralizes event polling and maps user keystrokes to actions.


### Systems & Data Persistence (src/systems/)

The systems package handles external data loading, configuration parsing, and local data persistence, enforcing a zero-crash policy for external file operations:

* config_parser.py (Resilient Config Parser):

    Comment Preprocessing: Strips # lines before JSON parsing.
    Self-Healing Validation: Uses Pydantic to replace individual invalid or out-of-bounds fields with safe defaults while preserving valid keys—guaranteeing zero crashes from bad config files.

* highscore.py (High Score Management):

    Top 10 Storage: Manages score persistence (highscores.json) with strict guards (1–10 char names, non-negative integer scores).
    Anti-Tampering Resilience: Purges corrupted or hand-edited JSON files and resets to a clean table to prevent UI crashes.
---

## General Software Architecture

The project follows MVC with dependency injection, split cleanly along the model/view boundary:

```
pac-man.py  ──► src/app.py  (orchestrator: main loop, dt, application FSM)
                    │
                    ▼
            src/states.py  (GameState enum + entity contract — shared interface)
                    │
        ┌───────────┴────────────┐
        ▼                        ▼
  src/core/ + src/entities/   src/ui/ + src/systems/ + src/level_manager/
  (Model — zero Pygame)       (View/Controller — reads model, never mutates it)
```

**`core/` and `entities/`** contain the entire simulation: `game.py` owns the world state and `update(dt)`, `level.py` owns a single level's grid/pacgums/timer, `progression.py` owns the sequence of levels and persistent score/lives. `entity.py`, `player.py`, `ghost.py`, and `collectibles.py` implement the actors. None of this layer imports Pygame — it can be reasoned about and tested as plain Python.

**`ui/`, `systems/`, and `level_manager/`** contain everything else: `renderer.py` reads `px/py` and `sprite_id` off the model to draw it and never writes back; `play_screen.py` orchestrates the in-game screen while `menus/` holds one file per screen (main menu, pause, highscores, instructions, end screens) instead of one large menu module; `input_handler.py` translates keystrokes into intentions rather than mutating entities directly; `config_parser.py` and `highscore.py` handle persistence; `maze_loader.py` adapts the external `A-Maze-ing` wheel to what `core/` expects.

The bridge between the two halves is the **entity contract** in `states.py`: every entity exposes `cell`, `px`/`py`, `direction`, and `sprite_id`; `Player` additionally exposes `lives`; `Ghost` additionally exposes its FSM `state`. It's the only file both sides needed to agree on before writing anything else — once it was fixed, the simulation and the rendering/data layers could move independently.

---

## Project Structure

```
pacman/
├── pac-man.py                          # Entry point (exactly 1 arg: the config file)
├── config.json                         # Example configuration
├── mazegenerator-00001-py3-none-any.whl # Assigned A-Maze-ing build, installed via `make install`
├── Makefile                            # install / run / debug / test / clean / lint
├── pyproject.toml                      # Dependencies
├── uv.lock
│
├── project_management/
├── packaging/                          # PyInstaller/Steam-Itch.io build
│
└── src/
    ├── app.py                          # Main loop, dt, application-level FSM
    ├── states.py                       # GameState enum + entity contract
    │
    ├── assets/images/                  # blinky, pinky, inky, clyde, pacman, frightened sprites
    │
    ├── core/                           # Simulation — no Pygame
    │   ├── game.py                     # World state, update(dt), ghost wave/frighten logic
    │   ├── level.py                    # Grid, pacgums, timer, win condition
    │   └── progression.py              # Level sequence, seeding, persistent score/lives
    │
    ├── entities/
    │   ├── entity.py                   # Base class: cell, px/py, direction
    │   ├── player.py                   # Movement, input buffering, lives, cheat flags
    │   ├── ghost.py                    # FSM: chase / scatter / frightened / eaten
    │   └── collectibles.py             # Pacgum, SuperPacgum
    │
    ├── level_manager/
    │   └── maze_loader.py              # Adapter for the external A-Maze-ing wheel
    │
    ├── systems/
    │   ├── config_parser.py            # Self-healing JSON configuration parser
    │   └── highscore.py                # Top 10 persistence & anti-tampering validation
    │
    └── ui/
        ├── renderer.py                 # Draws the model, never mutates it
        ├── play_screen.py              # In-game screen orchestration
        ├── hud.py                      # Score, lives, level, time remaining
        ├── input_handler.py            # Keys → intentions
        └── menus/                      # One screen per file
            ├── base_screen.py          # Abstract base class for all screens
            ├── base_score_entry.py     # Polymorphic database for entering scores
            ├── main_menu.py            # main menu
            ├── pause_menu.py           # pause menu
            ├── highscores_menu.py      # High Scores Table
            ├── instructions_menu.py    # Controls/Instructions Screen
            └── end_screens.py          # Game Over / Victory Screens
```

---

## Project Management

Work was split by ownership rather than by ticket: one programmer owned the simulation (`core/`, `entities/`), the other owned systems, UI, and data (`ui/`, `systems/`, `level_manager/`). The entity contract in `states.py` was fixed before any other code was written, specifically so both sides could build independently without merge conflicts on shared logic.

Development went through four phases: fixing the contract and skeleton first, then a minimal vertical slice (player moving on a real maze), then the playable core (collisions, ghosts, rendering), then systems and polish (menus, highscores, packaging). Each phase ended with an integration checkpoint instead of leaving everything to merge at the end.

Timeline, risk analysis, and team organization notes are being written up in `project_management/`; packaging to a public platform and the pytest suite are the remaining open items before submission.

---

## Resources

### References

- [Pygame documentation](https://www.pygame.org/docs/)
- [Pac-Man ghost AI — how the original arcade ghosts actually decide where to go](https://gameinternals.com/understanding-pac-man-ghost-behavior)
- [Fix Your Timestep! — Gaffer On Games (delta time and frame-independent movement)](https://gafferongames.com/post/fix_your_timestep/)
- [Finite State Machines for game AI](https://gameprogrammingpatterns.com/state.html)

### AI usage

AI was used strictly as a Socratic mentor to validate architectural decisions, clarify OOP concepts, and assist in structuring this documentation safely.