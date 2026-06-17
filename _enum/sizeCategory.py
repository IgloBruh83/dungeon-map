from enum import Enum

class SizeCategory(Enum):
    TINY = ("Tiny", 5)
    SMALL = ("Small", 10)
    MEDIUM = ("Medium", 10)
    LARGE = ("Large", 20)
    HUGE = ("Huge", 30)
    GARGANTUAN = ("Gargantuan", 40)
    COLOSSAL = ("Colossal", 60)

    def __init__(self, label: str, cell_size: int):
        self.label = label
        self.cell_size = cell_size

    @classmethod
    def from_label(cls, label_str: str) -> 'SizeCategory':
        for i in cls:
            if i.label == label_str:
                return i
        return cls.MEDIUM