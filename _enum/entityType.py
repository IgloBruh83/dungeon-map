from enum import Enum

class EntityType(Enum):
    ABERRATION = "Aberration"
    BEAST = "Beast"
    CELESTIAL = "Celestial"
    CONSTRUCT = "Construct"
    DRAGON = "Dragon"
    ELEMENTAL = "Elemental"
    FEY = "Fey"
    FIEND = "Fiend"
    GIANT = "Giant"
    HUMANOID = "Humanoid"
    MONSTROSITY = "Monstrosity"
    OOZE = "Ooze"
    PLANT = "Plant"
    UNDEAD = "Undead"

    @property
    def label(self) -> str:
        return self.value

    @classmethod
    def from_label(cls, label_str: str) -> 'CreatureType':
        for i in cls:
            if i.value == label_str:
                return i
        return cls.HUMANOID