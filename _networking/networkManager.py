import asyncio
import websockets
import json
import threading
from PySide6.QtCore import QObject, Signal, Slot

class NetworkManager(QObject):
    packageReceived = Signal(dict)
    connectionLost = Signal(str)
    connected = Signal()
    finished = Signal()

    def __init__(self, uri: str):
        super().__init__()
        self.uri = uri
        self.loop = None
        self.websocket = None
        self.running = False
        self._async_thread = None

    @Slot()
    def run(self):
        if self.running:
            return
        self.running = True
        self._async_thread = threading.Thread(target=self._start_asyncio_loop, daemon=True)
        self._async_thread.start()

    def _start_asyncio_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.connectAndListen())
        except Exception as e:
            if self.running:
                print(f"[Network] Async i/o loop interrupted: {e}")
        finally:
            self._cleanup_loop()

    async def connectAndListen(self):
        try:
            async with websockets.connect(self.uri, ping_interval=20, ping_timeout=20) as ws:
                self.websocket = ws
                print(f"[Network] Connected to {self.uri}")
                self.connected.emit()

                while self.running:
                    try:
                        message = await asyncio.wait_for(ws.recv(), timeout=1.0)
                        data = json.loads(message)
                        self.packageReceived.emit(data)
                    except asyncio.TimeoutError:
                        continue
                    except json.JSONDecodeError:
                        print("[Network] ERROR: Received JSON is invalid")

        except websockets.exceptions.ConnectionClosed as e:
            if self.running:
                self.connectionLost.emit(f"Connection closed: {e}")
        except Exception as e:
            if self.running:
                self.connectionLost.emit(f"Network exception: {e}")
        finally:
            self.websocket = None

    @Slot(dict)
    def sendPackage_slot(self, package: dict):
        if self.websocket and self.loop and self.running:
            try:
                json_string = json.dumps(package)
                asyncio.run_coroutine_threadsafe(
                    self.websocket.send(json_string),
                    self.loop
                )
            except Exception as e:
                print(f"[Network] Sending failed: {e}")

    @Slot()
    def stop(self):
        if not self.running:
            return

        print("[Network] Shutting down...")
        self.running = False
        if self.loop:
            if self.websocket:
                asyncio.run_coroutine_threadsafe(self.websocket.close(), self.loop)
            self.loop.call_soon_threadsafe(self.loop.stop)

    def _cleanup_loop(self):
        if not self.loop:
            return
        pending = asyncio.all_tasks(self.loop)
        if pending:
            self.loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        self.loop.close()
        try:
            self.finished.emit()
        except RuntimeError:
            pass