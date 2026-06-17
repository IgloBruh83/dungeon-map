from typing import Dict
from _models.entity import Entity

class Location:
    def __init__(self, dim_x, dim_y, map_bg: str, name: str = 'Unnamed Location'):
        self.name = name
        self.dim_x = dim_x
        self.dim_y = dim_y
        self.map_bg = map_bg
        self.entities: Dict[int, Entity] = {}

    def addEntity(self, entity: Entity):
        self.entities[entity.id] = entity
        entity.location = self

    def deleteEntity(self, entity_id: int) -> Entity | None:
        return self.entities.pop(entity_id, None)

    def save(self, forfeit_id=False) -> dict:
        return {
            'name': self.name,
            'dim': [self.dim_x, self.dim_y],
            'map_bg': self.map_bg,
            'entities': {str(ent_id): ent.save(forfeit_id) for ent_id, ent in self.entities.items()}
        }

    @classmethod
    def load(cls, data, entity_id_generator) -> 'Location':
        loc = cls(
            name=data.get('name'),
            dim_x=data['dim'][0],
            dim_y=data['dim'][1],
            map_bg=data.get('map_bg', "")
        )
        for ent_data in data.get('entities', {}).values():
            _ = Entity.load(ent_data, loc, entity_id_generator)
            loc.entities[_.id] = _

        return loc
