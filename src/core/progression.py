class GameProgression:
    """Tracks level progression up to the maximum level (10)."""

    def __init__(self) -> None:
        self.level_check: int = 1

    def next_level(self) -> bool:
        """Advance to the next level, or return False past the last one."""
        if self.level_check < 10:
            self.level_check += 1
            return True
        return False
