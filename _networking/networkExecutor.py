import os
from PySide6.QtCore import QObject, Signal, Slot

from _models.campaign import Campaign
from _models.entity import Entity
from _submodels.locationInstance import LocationInstance
from config import Config as cfg

class NetworkExecutor(QObject):
    sendRequest = Signal(dict)

    def __init__(self):
        super().__init__()

        self.handlers = {
            "SYNC_ALL" : self.hc_SYNC_ALL,
            "IDENTITY" : self.hc_IDENTITY,
            "ENTITY_MOVE" : self.hc_ENTITY_MOVE,
            "ENTITY_MOVE_FORBID" : self.hc_ENTITY_MOVE_FORBID,
            "ENTITY_ADD" : self.hc_ENTITY_ADD,
            "ENTITY_DELETE": self.hc_ENTITY_DELETE,
            "ENTITY_FLIPX": self.hc_ENTITY_FLIPX,
            "ENTITY_DAMAGE": self.hc_ENTITY_DAMAGE
        }

    def hc_ENTITY_DAMAGE(self, payload):
        entity_id = payload["id"]
        entity = cfg.campaign.location.entities[entity_id]
        entity.health = payload["health"]
        if hasattr(cfg, 'worldViewport') and cfg.worldViewport.tooltip.isVisible():
            cfg.worldViewport.showEntityTooltip(entity)
        # TODO: Use payload["type"] and payload["delta"] to make appearing damage numbers

    def hc_ENTITY_DELETE(self, payload):
        entity_id = payload["id"]
        cfg.campaign.location.deleteEntity(entity_id)
        cfg.worldViewport.getLocation.updateInstances()

    def hc_ENTITY_FLIPX(self, payload):
        entity_id = payload["id"]
        cfg.campaign.location.entities[entity_id].flipX = payload["flipX"]
        cfg.worldViewport.getLocation.entityInstances[entity_id].updateVisual()

    def hc_ENTITY_MOVE(self, payload):
        affected = cfg.campaign.location.entities[payload["id"]]
        affected.x = payload["pos"][0]
        affected.y = payload["pos"][1]
        cfg.worldViewport.getLocation.entityInstances[payload["id"]].updatePosition()

    def hc_ENTITY_ADD(self, payload):
        _ = Entity.load(payload, cfg.campaign.location, None)
        cfg.campaign.location.addEntity(_)
        cfg.worldViewport.getLocation.updateInstances()

    def hc_ENTITY_MOVE_FORBID(self, payload):
        instance = cfg.worldViewport.getLocation.entityInstances[payload["id"]]
        instance.forceDrop(payload["pos"][0], payload["pos"][1])

    def hc_SYNC_ALL(self, payload):
        if cfg.worldViewport.getLocation:
            _ = cfg.worldViewport.getLocation
            cfg.worldViewport.setLocation(None)
            _.deleteLater()
        synced_campaign = Campaign.load(payload)
        if synced_campaign:
            cfg.campaign = synced_campaign
        cfg.worldViewport.setLocation(LocationInstance(cfg.campaign.location))
        cfg.worldViewport.getLocation.updateBgGraphics()
        cfg.worldViewport.getLocation.updateInstances()

    def hc_IDENTITY(self, payload):
        print(f"[INFO] Identified with name [{payload["nickname"]}] as {payload['role']}")

    def sendEvent(self, event_type: str, payload: dict):
        package = {
            "event": event_type,
            "payload": payload,
        }
        self.sendRequest.emit(package)

    @Slot(dict)
    def onRecievedEvent(self, package: dict):
        try:
            event = package.get("event")
            payload = package.get("payload", {})
            if not event:
                print("[NetworkExecutor] Received JSON has no event")
                return
            handler = self.handlers.get(event)
            if handler:
                handler(payload)
            else:
                print(f"[NetworkExecutor] Received JSON has unknown event: [{event}]")
        except Exception as e:
            print(f"[NetworkExecutor] Exception while handling [{package.get('event')}]: {e}")


    @Slot(str)
    def onLostConnection(self, reason: str):
        print(f"[Network] Disconnected. {reason}")

    @Slot()
    def onConnected(self):
        print("[Network] Ready to send. Now listening...")

        from identity import Identity
        self.sendEvent("REQ_IDENTITY",{'nickname': Identity.nickname,
                                 'key': Identity.key if not Identity.forfeit_key else ''})