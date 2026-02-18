import asyncio
import json
import logging
from collections.abc import Callable, Coroutine
from typing import Any

from .config import HEOS_CLI_PORT, HEOS_TIMEOUT

logger = logging.getLogger(__name__)


class HeosEventListener:
    """Second HEOS TCP connection dedicated to receiving change events."""

    def __init__(self, host: str):
        self.host = host
        self.port = HEOS_CLI_PORT
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._connected = False
        self._task: asyncio.Task | None = None
        self._callback: Callable[[dict], Coroutine[Any, Any, None]] | None = None

    @property
    def connected(self) -> bool:
        return self._connected

    async def connect(self, callback: Callable[[dict], Coroutine[Any, Any, None]]) -> None:
        self._callback = callback
        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=HEOS_TIMEOUT,
            )
            self._connected = True
            logger.info("HEOS event listener connected to %s:%s", self.host, self.port)

            # Register for change events
            self._writer.write(
                b"heos://system/register_for_change_events?enable=on\r\n"
            )
            await self._writer.drain()

            # Read the registration response
            data = await asyncio.wait_for(
                self._reader.readuntil(b"\r\n"),
                timeout=HEOS_TIMEOUT,
            )
            logger.debug("Event registration response: %s", data.decode().strip())

            # Start listening loop
            self._task = asyncio.create_task(self._listen())
        except Exception:
            self._connected = False
            raise

    async def disconnect(self) -> None:
        self._connected = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        if self._writer:
            try:
                self._writer.close()
                await self._writer.wait_closed()
            except Exception:
                pass
            self._writer = None
            self._reader = None

    async def _listen(self) -> None:
        """Continuously read events and dispatch to callback."""
        assert self._reader is not None
        try:
            while self._connected:
                data = await self._reader.readuntil(b"\r\n")
                text = data.decode().strip()
                if not text:
                    continue
                try:
                    event = json.loads(text)
                    logger.debug("HEOS event: %s", text[:200])
                    if self._callback:
                        await self._callback(event)
                except json.JSONDecodeError:
                    logger.warning("Non-JSON HEOS event: %s", text[:200])
        except asyncio.CancelledError:
            raise
        except (ConnectionError, OSError) as e:
            logger.error("HEOS event listener disconnected: %s", e)
            self._connected = False
        except Exception:
            logger.exception("HEOS event listener error")
            self._connected = False
