# Risk Matrix & Mitigation

| Risk | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Risk 1: Coupling between Programmer A's simulation and Programmer B's UI** | **High.** Continuous blockages when changing entity attributes. | Strict definition of the entity contract in `src/states.py` from day one. The `renderer` strictly reads public attributes (`px`, `py`, `sprite_id`). |
| **Risk 2: Wall clipping due to lag spikes or high delta time values** | **Critical.** Breaks core gameplay mechanics. | Mandatory clamping of `dt` to a maximum of 0.05 seconds per tick (`min(dt, 0.05)`). |
| **Risk 3: Corrupt configuration or invalid JSON with `#` comments** | **Medium.** Application boot failure. | String preprocessing to strip `#` comment lines before parsing, automatically applying fallback default values without raising tracebacks. |
| **Risk 4: Accumulated type errors at the end of development** | **High.** Severe technical debt prior to delivery. | Integration of `make lint` (`flake8` + `mypy`) into daily workflow before every commit. |