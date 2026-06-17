from _models.location import Location

class Campaign:
    def __init__(self):

        self.DM_uid = None
        self.name = "Unnamed Campaign"
        self.description = "Empty campaign description"

        self.location: Location = Location(150,100,'bootcamp.jpg',"Bootcamp")

    def save(self, forfeit_id=False):
        return {
            'name': self.name,
            'DM_uid': self.DM_uid,
            'description': self.description,
            'location': self.location.save(forfeit_id)
        }

    @classmethod
    def load(cls, data, entity_id_generator=None) -> 'Campaign':
        _ = cls()
        _.DM_uid = data['DM_uid']
        _.name = data['name']
        _.description = data['description']
        _.location = Location.load(data['location'], entity_id_generator)

        return _
