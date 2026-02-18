import json
import logging

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections and broadcasts state updates."""

    def __init__(self):
        self._connections: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.append(ws)
        logger.info("WebSocket client connected (%d total)", len(self._connections))

    def disconnect(self, ws: WebSocket) -> None:
        if ws in self._connections:
            self._connections.remove(ws)
        logger.info("WebSocket client disconnected (%d total)", len(self._connections))

    async def broadcast(self, message: dict) -> None:
        """Send a JSON message to all connected clients."""
        if not self._connections:
            return
        text = json.dumps(message)
        disconnected = []
        for ws in self._connections:
            try:
                await ws.send_text(text)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self.disconnect(ws)

    async def send_to(self, ws: WebSocket, message: dict) -> None:
        """Send a JSON message to a specific client."""
        try:
            await ws.send_text(json.dumps(message))
        except Exception:
            self.disconnect(ws)
