import asyncio
import logging

from .denon_avr import DenonAVR
from .discovery import discover_avr
from .heos_client import HeosClient
from .heos_event_listener import HeosEventListener
from .models import AppState, NowPlaying
from .ws import WebSocketManager

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Owns all protocol clients, the state cache, and bridges events to WebSocket."""

    def __init__(self):
        self.ws_manager = WebSocketManager()
        self.avr: DenonAVR | None = None
        self.heos: HeosClient | None = None
        self.event_listener: HeosEventListener | None = None
        self.state = AppState()

    async def startup(self) -> None:
        """Discover AVR and establish all connections."""
        ip = await discover_avr()
        if not ip:
            logger.error("No Denon AVR found on network")
            return

        self.state.avr_ip = ip
        logger.info("Connecting to AVR at %s", ip)

        # Connect all clients in parallel
        self.avr = DenonAVR(ip)
        self.heos = HeosClient(ip)
        self.event_listener = HeosEventListener(ip)

        results = await asyncio.gather(
            self._connect_avr(),
            self._connect_heos(),
            return_exceptions=True,
        )
        for r in results:
            if isinstance(r, Exception):
                logger.error("Connection error: %s", r)

        self.state.connected = bool(
            self.avr and self.avr.connected
            or self.heos and self.heos.connected
        )

        # Fetch initial state
        if self.state.connected:
            await self._poll_initial_state()

    async def _connect_avr(self) -> None:
        if self.avr:
            try:
                await self.avr.connect()
            except Exception as e:
                logger.error("Failed to connect AVR telnet: %s", e)
                self.avr = None

    async def _connect_heos(self) -> None:
        if self.heos:
            try:
                await self.heos.connect()
                await self.heos.discover_player()
                self.state.player_id = self.heos.player_id
            except Exception as e:
                logger.error("Failed to connect HEOS: %s", e)
                self.heos = None
                return

        if self.event_listener:
            try:
                await self.event_listener.connect(self._on_heos_event)
            except Exception as e:
                logger.error("Failed to connect HEOS event listener: %s", e)
                self.event_listener = None

    async def _poll_initial_state(self) -> None:
        """Query current state from all clients."""
        try:
            if self.avr and self.avr.connected:
                results = await asyncio.gather(
                    self.avr.get_power(),
                    self.avr.get_volume(),
                    self.avr.get_mute(),
                    self.avr.get_sleep(),
                    self.avr.get_source(),
                    return_exceptions=True,
                )
                if not isinstance(results[0], Exception):
                    self.state.power = results[0]
                if not isinstance(results[1], Exception):
                    self.state.volume = results[1]
                if not isinstance(results[2], Exception):
                    self.state.mute = results[2]
                if not isinstance(results[3], Exception):
                    self.state.sleep = results[3]
                if not isinstance(results[4], Exception):
                    self.state.source = results[4]
        except Exception:
            logger.exception("Error polling AVR state")

        try:
            if self.heos and self.heos.connected:
                play_state = await self.heos.get_play_state()
                self.state.play_state = play_state

                np_data = await self.heos.get_now_playing()
                if np_data:
                    self.state.now_playing = NowPlaying(
                        type=np_data.get("type"),
                        song=np_data.get("song"),
                        album=np_data.get("album"),
                        artist=np_data.get("artist"),
                        image_url=np_data.get("image_url"),
                        station=np_data.get("station"),
                        mid=np_data.get("mid"),
                        qid=np_data.get("qid"),
                        sid=np_data.get("sid"),
                    )
        except Exception:
            logger.exception("Error polling HEOS state")

    async def shutdown(self) -> None:
        """Disconnect all clients."""
        tasks = []
        if self.event_listener:
            tasks.append(self.event_listener.disconnect())
        if self.heos:
            tasks.append(self.heos.disconnect())
        if self.avr:
            tasks.append(self.avr.disconnect())
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        self.state.connected = False

    async def rediscover(self) -> str | None:
        """Re-run SSDP discovery and reconnect."""
        await self.shutdown()
        await self.startup()
        return self.state.avr_ip

    async def update_state(self, force_broadcast=False, **kwargs) -> None:
        """Update cached state and broadcast changes via WebSocket."""
        changed = {}
        for key, value in kwargs.items():
            if hasattr(self.state, key):
                if getattr(self.state, key) != value or force_broadcast:
                    setattr(self.state, key, value)
                    changed[key] = value

        if changed:
            for key, value in changed.items():
                await self.ws_manager.broadcast({"type": key, "data": value})

    async def update_now_playing(self, data: dict) -> None:
        """Update now-playing state from HEOS payload."""
        np = NowPlaying(
            type=data.get("type"),
            song=data.get("song"),
            album=data.get("album"),
            artist=data.get("artist"),
            image_url=data.get("image_url"),
            station=data.get("station"),
            mid=data.get("mid"),
            qid=data.get("qid"),
            sid=data.get("sid"),
        )
        self.state.now_playing = np
        await self.ws_manager.broadcast({
            "type": "now_playing",
            "data": np.model_dump(),
        })

    async def get_full_state(self) -> dict:
        """Return the full cached state as a dict."""
        return self.state.model_dump()

    async def _on_heos_event(self, event: dict) -> None:
        """Handle incoming HEOS change events."""
        heos = event.get("heos", {})
        command = heos.get("command", "")
        message = heos.get("message", "")

        params = {}
        if message:
            for part in message.split("&"):
                if "=" in part:
                    k, v = part.split("=", 1)
                    params[k] = v

        logger.debug("HEOS event command=%s params=%s", command, params)

        if command == "event/player_state_changed":
            state = params.get("state")
            if state:
                await self.update_state(play_state=state)

        elif command == "event/player_now_playing_changed":
            # Re-fetch now playing
            if self.heos and self.heos.connected:
                try:
                    data = await self.heos.get_now_playing()
                    if data:
                        await self.update_now_playing(data)
                except Exception:
                    logger.exception("Error fetching now-playing after event")

        elif command == "event/player_now_playing_progress":
            pass  # Ignore progress events for now

        elif command == "event/player_volume_changed":
            level = params.get("level")
            mute = params.get("mute")
            if level is not None:
                try:
                    await self.update_state(volume=int(level))
                except ValueError:
                    pass
            if mute is not None:
                await self.update_state(mute="ON" if mute == "on" else "OFF")
