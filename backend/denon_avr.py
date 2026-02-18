import asyncio
import logging

from .config import (
    DENON_TELNET_PORT,
    POWER_ON_DELAY,
    TELNET_LOCK_TIMEOUT,
    TELNET_TIMEOUT,
)

logger = logging.getLogger(__name__)


class DenonAVR:
    """Async client for Denon AVR telnet protocol (port 23)."""

    def __init__(self, host: str):
        self.host = host
        self.port = DENON_TELNET_PORT
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._lock = asyncio.Lock()
        self._connected = False

    @property
    def connected(self) -> bool:
        return self._connected

    async def connect(self) -> None:
        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=TELNET_TIMEOUT,
            )
            self._connected = True
            logger.info("Connected to Denon AVR telnet at %s:%s", self.host, self.port)
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

    async def _send_command(self, command: str, expect_multi: bool = False) -> list[str]:
        """Send a command and return response lines."""
        async with asyncio.timeout(TELNET_LOCK_TIMEOUT):
            async with self._lock:
                return await self._send_raw(command, expect_multi)

    async def _send_raw(self, command: str, expect_multi: bool) -> list[str]:
        if not self._writer or not self._reader:
            raise ConnectionError("Not connected to AVR")

        try:
            self._writer.write(f"{command}\r".encode())
            await self._writer.drain()
            logger.debug("Sent: %s", command)

            lines: list[str] = []
            while True:
                try:
                    data = await asyncio.wait_for(
                        self._reader.readuntil(b"\r"),
                        timeout=TELNET_TIMEOUT,
                    )
                    line = data.decode().strip()
                    if line:
                        lines.append(line)
                        logger.debug("Recv: %s", line)
                    if not expect_multi or len(lines) >= 2:
                        # For multi-line responses, read up to 2 lines then stop
                        break
                except asyncio.TimeoutError:
                    break

            return lines
        except (ConnectionError, OSError) as e:
            logger.error("AVR communication error: %s", e)
            self._connected = False
            raise

    def _parse_response(self, lines: list[str], prefix: str) -> str | None:
        for line in lines:
            if line.startswith(prefix):
                return line[len(prefix):]
        return None

    # --- Power ---

    async def get_power(self) -> str | None:
        """Returns 'ON' or 'STANDBY'."""
        lines = await self._send_command("PW?")
        val = self._parse_response(lines, "PW")
        return val

    async def power_on(self) -> str:
        lines = await self._send_command("PWON")
        # Delay after power on per spec
        await asyncio.sleep(POWER_ON_DELAY)
        return self._parse_response(lines, "PW") or "ON"

    async def power_off(self) -> str:
        lines = await self._send_command("PWSTANDBY")
        return self._parse_response(lines, "PW") or "STANDBY"

    # --- Volume ---

    async def get_volume(self) -> int | None:
        """Returns volume level (0-98)."""
        lines = await self._send_command("MV?", expect_multi=True)
        val = self._parse_response(lines, "MV")
        if val is None:
            return None
        # Filter out "MAX" lines — volume response can be "MV45" followed by "MVMAX 80"
        val = val.strip()
        if val.startswith("MAX"):
            # Look for the non-MAX line
            for line in lines:
                if line.startswith("MV") and "MAX" not in line:
                    val = line[2:].strip()
                    break
            else:
                return None
        try:
            # Volume can be 2 or 3 digits: "45" = 45, "455" = 45.5
            if len(val) == 3:
                return int(val[:2])
            return int(val)
        except ValueError:
            return None

    async def set_volume(self, level: int) -> int:
        cmd = f"MV{level:02d}"
        await self._send_command(cmd, expect_multi=True)
        return level

    async def volume_up(self) -> None:
        await self._send_command("MVUP", expect_multi=True)

    async def volume_down(self) -> None:
        await self._send_command("MVDOWN", expect_multi=True)

    # --- Mute ---

    async def get_mute(self) -> str | None:
        """Returns 'ON' or 'OFF'."""
        lines = await self._send_command("MU?")
        return self._parse_response(lines, "MU")

    async def mute_on(self) -> str:
        await self._send_command("MUON")
        return "ON"

    async def mute_off(self) -> str:
        await self._send_command("MUOFF")
        return "OFF"

    async def toggle_mute(self) -> str:
        current = await self.get_mute()
        if current == "ON":
            return await self.mute_off()
        return await self.mute_on()

    # --- Sleep Timer ---

    async def get_sleep(self) -> str | None:
        """Returns minutes as string or 'OFF'."""
        lines = await self._send_command("SLP?")
        return self._parse_response(lines, "SLP")

    async def set_sleep(self, minutes: int) -> str:
        if minutes == 0:
            await self._send_command("SLPOFF")
            return "OFF"
        cmd = f"SLP{minutes:03d}"
        await self._send_command(cmd)
        return str(minutes)

    # --- Source / Input ---

    async def get_source(self) -> str | None:
        """Returns current input source like 'TV', 'NET', 'SAT/CBL', etc."""
        lines = await self._send_command("SI?")
        return self._parse_response(lines, "SI")

    async def set_source(self, source: str) -> str:
        cmd = f"SI{source}"
        await self._send_command(cmd)
        return source
