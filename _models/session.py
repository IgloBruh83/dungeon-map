import json
from typing import Set, Dict

from _models.campaign import Campaign


class Session:
    def __init__(self, campaign_file: str):

        self._next_entity_id = 1
        self.clients: Set = set()
        self.campaign = None

    def load(self, campaign_file: str):
        try:
            with open(f"{campaign_file}.json", "r", encoding="utf-8") as file:
                data = json.load(file)
                self.campaign = Campaign.load(data, entity_id_generator=self.getNextEntityId)
        except Exception as e:
            print(e)
            return False
        return True

    def save(self, campaign_file: str):
        if self.campaign is None:
            return False
        try:
            data = self.campaign.save(forfeit_id=True)
            with open(f"{campaign_file}.json", "w") as file:
                json.dump(data, file)
        except Exception as e:
            print(e)
            return False
        return True

    def getNextEntityId(self) -> int:
        current = self._next_entity_id
        self._next_entity_id += 1
        return current

    def registerClient(self, client_connection):
        self.clients.add(client_connection)

    def unregisterClient(self, client_connection):
        self.clients.discard(client_connection)