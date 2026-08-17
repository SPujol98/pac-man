class GameProgression():
    """Manage the sequence of game levels and progression state.

    Provides functionality to advance to the next level if the maximum
    limit (10) is not reached, returning True on success or False if
    the game is completed.
    """
    def __init__(self) -> None:
        self.level_check: int = 1

    def next_level(self) -> bool:
        if self.level_check < 10:
            self.level_check += 1
            return True
        return False
