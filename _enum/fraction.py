from enum import Enum

class Fraction(Enum):
    NPC = ("NPC", '#A9A9A9')
    NEUTRAL = ("Neutral", '#FFB347')
    PARTY = ("Party", '#4CAF50')
    ALLY = ("Ally", '#29B6F6')
    ENEMY = ("Enemy", '#E53935')
    BOSS = ("Boss", '#8B0000')

    def __init__(self, label: str, color: str):
        self.label = label
        self.color = color

    @classmethod
    def from_label(cls, label_str: str) -> 'Fraction':
        for i in cls:
            if i.label == label_str:
                return i
        return cls.NEUTRAL