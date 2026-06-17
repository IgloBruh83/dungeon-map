from enum import Enum

class DamageType(Enum):
    TRUE = ("True", '#FFFFFF')
    BLUDGEONING = ("Bludgeoning", '#FFFFFF')
    PIERCING = ("Piercing", '#FFFFFF')
    SLASHING = ("Slashing", '#FFFFFF')
    ACID = ("Acid", '#FFFFFF')
    FIRE = ("Fire", '#FFFFFF')
    COLD = ("Cold", '#FFFFFF')
    FORCE = ("Force", '#FFFFFF')
    LIGHTNING = ("Lightning", '#FFFFFF')
    NECROTIC = ("Necrotic", '#FFFFFF')
    POISON = ("Poison", '#FFFFFF')
    PSYCHIC = ("Psychic", '#FFFFFF')
    RADIANT = ("Radiant", '#FFFFFF')
    THUNDER = ("Thunder", '#FFFFFF')

    def __init__(self, label: str, color: str):
        self.label = label
        self.color = color

    @classmethod
    def from_label(cls, label_str: str) -> 'DamageType':
        for i in cls:
            if i.label == label_str:
                return i
        return cls.TRUE