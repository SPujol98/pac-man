## Acceptance Test Plan & Bug Log

### Acceptance Test Plan

| ID | Module / Feature | Test Case | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC01** | `config_parser` | Load JSON configuration file containing `#` comments and out-of-range keys. | Parses successfully using default values and applies value clamping. | Passed |
| **TC02** | `player` | Press directional turn key prior to reaching a grid intersection. | Input buffer stores turn intention and applies it when aligned with cell center. | Passed |
| **TC03** | `ghost` / FSM | Consume SuperPacgum collectible. | Ghosts transition to `FRIGHTENED`, change to `EATEN` when touched, and return to home corner. | Passed |
| **TC04** | `progression` | Complete all objectives in Level 1. | Preserves score/lives, advances to Level 2, and generates layout using random seed. | Passed |
| **TC05** | `highscore` | Record a new high score entry with valid alphanumeric player name. | Entry persists in sorted Top 10 JSON file on disk. | Passed |
| **TC06** | `cheat_mode` | Enable invincibility toggle key. | Player receives no damage or life penalty upon colliding with active ghosts. | Passed |

### Bug Log & Fixes

* **Bug #1: Mypy optional type error (`Game | None`) in `PlayScreen`[cite: 1]**
  * *Issue:* `mypy` flagged potential `NoneType` access when querying `self.game` attributes in screen lifecycle methods.
  * *Fix:* Implemented early guard clauses (`if self.game is None: return`) to enforce type narrowing across all active screen hooks.
* **Bug #2: Ghost wall clipping under heavy CPU load**
  * *Issue:* Extreme frame rate drops caused ghosts to leap over wall tiles due to unconstrained delta time.
  * *Fix:* Enforced strict frame delta clamping (`min(dt, 0.05)`) in the main `app.py` update loop.

---

## 6. Blocking Points & Conflict Resolution

* **Blocking Point 1: Incompatibility between standard JSON format and `#` comments.**
  * *Origin:* Project specification required supporting `#` comments in `config.json`, causing standard `json.loads` to fail.
  * *Resolution:* updated `config_parser.py` to filter out lines starting with `#` prior to JSON parsing.
* **Blocking Point 2: Desynchronization between rendering continuous positions and AI logic.**
  * *Origin:* Continuous pixel movement caused AI entities to attempt navigation decisions mid-corridor rather than at intersections.
  * *Resolution:* **Programmer A** reinforced cell-center alignment checks: AI decisions and collision evaluations execute strictly when entities align with cell centers.