import asyncio
import json
import logging

from .config import HEOS_CLI_PORT, HEOS_TIMEOUT

logger = logging.getLogger(__name__)


def _heos_encode(value: str) -> str:
    """Encode special characters for HEOS command values."""
    return value.replace("%", "%25").replace("&", "%26").replace("=", "%3D")


class HeosClient:
    """Async client for HEOS CLI protocol (port 1255). Used for commands."""

    def __init__(self, host: str):
        self.host = host
        self.port = HEOS_CLI_PORT
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._lock = asyncio.Lock()
        self._connected = False
        self.player_id: int | None = None

    @property
    def connected(self) -> bool:
        return self._connected

    async def connect(self) -> None:
        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=HEOS_TIMEOUT,
            )
            self._connected = True
            logger.info("HEOS command client connected to %s:%s", self.host, self.port)
        except Exception:
            self._connected = False
            raise

    async def disconnect(self) -> None:
        self._connected = False
        if self._writer:
            try:
                self._writer.close()
                await self._writer.wait_closed()
            except Exception:
                pass
            self._writer = None
            self._reader = None

    async def _send(self, command: str) -> dict:
        """Send a HEOS command and return parsed JSON response. Auto-reconnects once on failure."""
        async with self._lock:
            try:
                return await self._send_raw(command)
            except (ConnectionError, OSError, RuntimeError) as e:
                logger.warning("HEOS send failed (%s), reconnecting...", e)
                await self._reconnect()
                return await self._send_raw(command)

    async def _reconnect(self) -> None:
        """Close the dead connection and open a fresh one."""
        self._connected = False
        if self._writer:
            try:
                self._writer.close()
                await self._writer.wait_closed()
            except Exception:
                pass
            self._writer = None
            self._reader = None
        self._reader, self._writer = await asyncio.wait_for(
            asyncio.open_connection(self.host, self.port),
            timeout=HEOS_TIMEOUT,
        )
        self._connected = True
        logger.info("HEOS command client reconnected to %s:%s", self.host, self.port)

    async def _send_raw(self, command: str) -> dict:
        if not self._writer or not self._reader:
            raise ConnectionError("HEOS not connected")

        try:
            self._writer.write(f"{command}\r\n".encode())
            await self._writer.drain()
            logger.debug("HEOS sent: %s", command)

            data = await asyncio.wait_for(
                self._reader.readuntil(b"\r\n"),
                timeout=HEOS_TIMEOUT,
            )
            text = data.decode().strip()
            logger.debug("HEOS recv: %s", text[:200])

            result = json.loads(text)
            return result
        except (ConnectionError, OSError) as e:
            logger.error("HEOS communication error: %s", e)
            self._connected = False
            raise

    @staticmethod
    def _parse_message(msg: str) -> dict:
        """Parse HEOS message string like 'pid=123&result=success' into dict."""
        if not msg:
            return {}
        params = {}
        for part in msg.split("&"):
            if "=" in part:
                k, v = part.split("=", 1)
                params[k] = v
        return params

    def _check_result(self, response: dict) -> bool:
        heos = response.get("heos", {})
        msg = self._parse_message(heos.get("message", ""))
        return msg.get("result", "") == "success" or "result" not in msg

    # --- Players ---

    async def get_players(self) -> list[dict]:
        resp = await self._send("heos://player/get_players")
        return resp.get("payload", [])

    async def discover_player(self) -> int | None:
        """Find the first player and store its PID."""
        players = await self.get_players()
        if players:
            self.player_id = players[0].get("pid")
            logger.info("Discovered HEOS player PID: %s", self.player_id)
            return self.player_id
        logger.warning("No HEOS players found")
        return None

    # --- Now Playing ---

    async def get_now_playing(self) -> dict:
        if self.player_id is None:
            return {}
        resp = await self._send(
            f"heos://player/get_now_playing_media?pid={self.player_id}"
        )
        return resp.get("payload", {})

    # --- Play State ---

    async def get_play_state(self) -> str | None:
        if self.player_id is None:
            return None
        resp = await self._send(
            f"heos://player/get_play_state?pid={self.player_id}"
        )
        msg = self._parse_message(resp.get("heos", {}).get("message", ""))
        return msg.get("state")

    async def set_play_state(self, state: str) -> str:
        if self.player_id is None:
            raise ConnectionError("No HEOS player discovered")
        await self._send(
            f"heos://player/set_play_state?pid={self.player_id}&state={state}"
        )
        return state

    # --- Browse ---

    async def browse_tunein(self, cid: str | None = None) -> list[dict]:
        if cid:
            cmd = f"heos://browse/browse?sid=3&cid={_heos_encode(cid)}"
        else:
            cmd = "heos://browse/browse?sid=3"
        resp = await self._send(cmd)
        return resp.get("payload", [])

    async def browse_favorites(self) -> list[dict]:
        resp = await self._send("heos://browse/browse?sid=1028")
        return resp.get("payload", [])

    async def play_station(self, sid: int, cid: str, mid: str, name: str) -> bool:
        if self.player_id is None:
            raise ConnectionError("No HEOS player discovered")
        cmd = (
            f"heos://browse/play_station?pid={self.player_id}"
            f"&sid={sid}&cid={_heos_encode(cid)}"
            f"&mid={_heos_encode(mid)}&name={_heos_encode(name)}"
        )
        resp = await self._send(cmd)
        return self._check_result(resp)

    async def play_preset(self, preset: int) -> bool:
        if self.player_id is None:
            raise ConnectionError("No HEOS player discovered")
        resp = await self._send(
            f"heos://browse/play_preset?pid={self.player_id}&preset={preset}"
        )
        return self._check_result(resp)

    async def search_tunein(self, query: str) -> list[dict]:
        # HEOS search: first get search criteria for TuneIn
        # Then search with the criteria. For TuneIn, scid=1 (stations)
        search_cmd = (
            f"heos://browse/search?sid=3&search={_heos_encode(query)}&scid=1"
        )
        resp = await self._send(search_cmd)
        return resp.get("payload", [])
