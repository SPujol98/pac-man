class GameProgression():
    def __init__(self) -> None:
        self.level_check: int = 1

    def next_level(self) -> bool:
        if self.level_check < 10:
            self.level_check += 1
            return True
        return False
