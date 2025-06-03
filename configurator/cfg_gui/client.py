import time
import asyncio
import threading
import websockets
from typing import Any, Callable, Optional
from multiprocessing import current_process

from PySide6.QtCore import QMetaObject, Qt
from PySide6.QtWidgets import QMainWindow
from .protocol import Dict, Protocol

SERVER_URL = "ws://localhost:20409"


class Client(threading.Thread):

    def __init__(self, mainWindow: QMainWindow):
        super().__init__(name="Client")
        self.mainWindow = mainWindow
        self.running = False
        self.appId = str(current_process().pid)
        self.protocol = Protocol()
        self.loop = asyncio.new_event_loop()
        self.send_ready = False

    @property
    def ws(self):
        if not hasattr(self, "_ws"):
            raise RuntimeError("ws is already set")
        return self._ws

    @ws.setter
    def ws(self, ws: websockets.WebSocketClientProtocol):
        self._ws = ws

    def stop(self):
        self.running = False
        self.send_ready = False

    def run(self):
        asyncio.set_event_loop(self.loop)

        async def async_connect():
            try:
                self.running = True
                self.ws = await websockets.connect(SERVER_URL)
                await self.send_message("first", {"appId": self.appId, "winId": int(self.mainWindow.winId())})
                await self.receive_messages(timeout=None)
                self.send_ready = True
                heartbeat_task = asyncio.create_task(self.send_heartbeats())
                command_task = asyncio.create_task(self.handle_command())
                await asyncio.gather(heartbeat_task, command_task)
            except Exception as e:
                print(f"连接错误: {e}")
            finally:
                self.running = False
                if self.ws is not None:
                    await self.ws.close()

        self.loop.run_until_complete(async_connect())

    def send(self, message_type: str, payload: Dict[str, Any]):

        async def wait_for_send_ready(message_type, payload):
            while self.running and not self.send_ready:
                await asyncio.sleep(0.01)
            await self.send_message(message_type, payload)
        asyncio.run_coroutine_threadsafe(wait_for_send_ready(message_type, payload), loop=self.loop)

    async def send_message(self, message_type: str, payload: Dict[str, Any]):
        data = self.protocol.encode_message(message_type, payload, self.appId)
        await self.ws.send(data)

    async def send_heartbeats(self):
        while self.running and self.send_ready:
            await self.send_message("heartbeat", {"timestamp": time.time()})
            await asyncio.sleep(1)

    async def receive_messages(self, timeout: Optional[int] = 1):
        try:
            data = await asyncio.wait_for(self.ws.recv(), timeout)
            return self.protocol.decode_message(data, is_client=True)
        except asyncio.TimeoutError:
            return None

    async def handle_command(self):
        while self.running:
            message = await self.receive_messages()
            if message is None:
                continue
            message_type = message["type"]
            payload = message.get("payload", {}) or {}
            if message_type == "command" and self.command_handle:
                if payload.get("action") == "shutdown":
                    self.invoke_method(self.mainWindow, "close")
                else:
                    return await self.command_handle(payload)
            elif message_type == "query" and self.query_handle:
                return await self.query_handle(payload)
            elif message_type == "register" and self.register_handle:
                return await self.register_handle(payload)
            else:
                raise KeyError(f"handler_type {message_type} not already registered")

    def registe_handle(self, handle_type: str, handle: Callable):
        if not asyncio.iscoroutinefunction(handle):
            handle = asyncio.coroutine(handle)
        if handle_type == "command" and self.command_handle is None:
            self.command_handle = handle
        elif handle_type == "query" and self.query_handle is None:
            self.query_handle = handle
        elif handle_type == "register" and self.register_handle is None:
            self.register_handle = handle
        else:
            raise KeyError(f"handle_{handle_type} already registered")

    def invoke_method(self, obj, method, *args):
        QMetaObject.invokeMethod(obj, method, Qt.ConnectionType.QueuedConnection, *args)
