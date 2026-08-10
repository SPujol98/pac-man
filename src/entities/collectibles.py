from src.entities.entity import Collectible


class Pacgum(Collectible):
    def __init__(self, cell: tuple[int, int], points: int):
        super().__init__(cell, "pacgum", points)


class SuperPacgum(Collectible):
    def __init__(self, cell: tuple[int, int], points: int) -> None:
        super().__init__(cell, "superpacgum", points)
