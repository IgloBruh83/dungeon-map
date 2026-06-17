import asyncio

import websockets
import json

from _models.session import Session
from _models.campaign import Campaign
from _models.entity import Entity


class DungeonMapServer:
    def __init__(self, host="0.0.0.0", port=2025, campaign_file="current_campaign"):
        self.host = host
        self.port = port
        self.clients = {}  # websocket -> {"role": "PLAYER", "name": "Unknown"}

        self.session = Session(campaign_file)
        if not self.session.load(campaign_file):
            print(f"[WARNING] Failed to load {campaign_file}. Creating an empty one.")
            self.session.campaign = Campaign()

        self.handlers = {
            'REQ_IDENTITY': self.h_IDENTITY,
            'REQ_ENTITY_MOVE': self.h_ENTITY_MOVE,
            'REQ_ENTITY_MOVE_END': self.h_ENTITY_MOVE_END,
            'REQ_ENTITY_ADD': self.h_REQ_ENTITY_ADD,
            'REQ_ENTITY_DELETE': self.h_REQ_ENTITY_DELETE,
            'REQ_ENTITY_FLIPX': self.h_REQ_ENTITY_FLIPX,
            'REQ_ENTITY_DAMAGE': self.h_REQ_ENTITY_DAMAGE
        }

    async def h_REQ_ENTITY_DAMAGE(self, websocket, payload):
        if self.clients[websocket]["role"] != "DM":
            return
        entity_id = payload["id"]
        taken = self.session.campaign.location.entities[entity_id].takeDamage(payload["amount"], payload["type"])
        await self.broadcast("ENTITY_DAMAGE",
                             {"id": entity_id, "health": self.session.campaign.location.entities[entity_id].health,
                            "delta": taken, "type": payload["type"]})

    async def h_REQ_ENTITY_DELETE(self, websocket, payload):
        if self.clients[websocket]["role"] != "DM":
            return
        entity_id = payload["id"]
        self.session.campaign.location.deleteEntity(entity_id)
        await self.broadcast("ENTITY_DELETE", payload)

    async def h_REQ_ENTITY_FLIPX(self, websocket, payload):
        entity_id = payload["id"]
        self.session.campaign.location.entities[entity_id].flipX = payload["flipX"]
        await self.broadcast("ENTITY_FLIPX", payload)


    async def h_REQ_ENTITY_ADD(self, websocket, payload):
        if self.clients[websocket]["role"] != "DM":
            return
        _ = Entity.load(payload, self.session.campaign.location, self.session.getNextEntityId)
        self.session.campaign.location.addEntity(_)
        to_send = _.save(forfeit_id=False)
        await self.broadcast("ENTITY_ADD", to_send)

    async def h_ENTITY_MOVE(self, websocket, payload):
        entity_affected = self.session.campaign.location.entities[payload["id"]]
        if entity_affected.grabbedBy is not None:
            if self.clients[websocket]["role"] != "DM" and entity_affected.grabbedBy != websocket:
                await self.send_to(websocket, "ENTITY_MOVE_FORBID",
                             {"id": payload["id"],
                              "pos": [entity_affected.x, entity_affected.y]})
                return
        entity_affected.grabbedBy = websocket
        entity_affected.x = payload["pos"][0]
        entity_affected.y = payload["pos"][1]
        await self.broadcast("ENTITY_MOVE", payload, exclude=websocket)

    async def h_ENTITY_MOVE_END(self, websocket, payload):
        await self.h_ENTITY_MOVE(websocket, payload)
        entity_affected = self.session.campaign.location.entities[payload["id"]]
        if entity_affected.grabbedBy is not None:
            if self.clients[websocket]["role"] != "DM" and entity_affected.grabbedBy != websocket:
                return
        entity_affected.grabbedBy = None

    async def h_IDENTITY(self, websocket, payload):
        _nickname = payload.get("nickname")
        _key = payload.get("key")
        _reference_key = open("DM_key.hex", 'r').read()
        self.clients[websocket] = {"name": _nickname,
                                   "role": "DM" if _key==_reference_key else "PLAYER",}
        await self.send_to(websocket, "IDENTITY",
                     {"nickname": self.clients[websocket]["name"],
                              "role": self.clients[websocket]["role"]})
        campaign_to_send = self.session.campaign.save(forfeit_id=False)
        await self.send_to(websocket, "SYNC_ALL", payload=campaign_to_send)

    async def broadcast(self, event_type, payload, exclude=None):
        if not self.clients:
            return
        package = json.dumps({"event": event_type, "payload": payload})
        recipients = [ws for ws in self.clients if ws != exclude]
        if recipients:
            websockets.broadcast(recipients, package)

    async def send_to(self, ws, event_type, payload):
        package = json.dumps({"event": event_type, "payload": payload})
        await ws.send(package)

    async def handler(self, websocket):
        """Головний цикл обробки підключення клієнта"""
        _port = list(websocket.remote_address)[1]
        self.clients[websocket] = {"name":_port, "role":"FORBIDDEN"}
        self.session.registerClient(websocket)
        print(f"[+] Client connected: {websocket.remote_address}")

        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    event = data.get("event")
                    payload = data.get("payload", {})

                    handler = self.handlers.get(event)
                    if handler:
                        await handler(websocket, payload)
                    else:
                        print(f"[WARNING] Unknown event from {websocket.remote_address}: {event}")

                except json.JSONDecodeError:
                    print("[ERROR] Received JSON is invalid")
                except Exception as e:
                    print(f"[ERROR] Exception while handling an event: {e}")

        except websockets.exceptions.ConnectionClosedError:
            print(f"[-] Connection closed: {websocket.remote_address}")
        finally:
            self.session.unregisterClient(websocket)
            for ent in self.session.campaign.location.entities.values():
                if ent.grabbedBy == websocket:
                    ent.grabbedBy = None
            if websocket in self.clients:
                del self.clients[websocket]
            print(f"[-] Client disconnected: {websocket.remote_address}")


    async def start(self):
        print(f"[INFO] Server started on ws://{self.host}:{self.port}")
        async with websockets.serve(self.handler, self.host, self.port):
            await asyncio.Future()


if __name__ == "__main__":
    server = DungeonMapServer(port=2026, campaign_file="test")
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("[INFO] Server stopped (KeyboardInterrupt).")