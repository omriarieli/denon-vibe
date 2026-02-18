import asyncio
import logging
import socket

from .config import SSDP_MULTICAST_ADDR, SSDP_PORT, SSDP_TIMEOUT

logger = logging.getLogger(__name__)

SSDP_REQUEST = (
    "M-SEARCH * HTTP/1.1\r\n"
    f"HOST: {SSDP_MULTICAST_ADDR}:{SSDP_PORT}\r\n"
    'MAN: "ssdp:discover"\r\n'
    "MX: 3\r\n"
    "ST: urn:schemas-denon-com:device:ACT-Denon:1\r\n"
    "\r\n"
)


class _SSDPProtocol(asyncio.DatagramProtocol):
    def __init__(self, future: asyncio.Future):
        self._future = future

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        response = data.decode(errors="replace")
        if "Denon" in response or "HEOS" in response or "denon" in response.lower():
            if not self._future.done():
                self._future.set_result(addr[0])

    def error_received(self, exc: Exception) -> None:
        logger.warning("SSDP error: %s", exc)

    def connection_lost(self, exc: Exception | None) -> None:
        pass


async def discover_avr() -> str | None:
    """Discover a Denon AVR on the local network via SSDP. Returns IP or None."""
    loop = asyncio.get_running_loop()
    future: asyncio.Future[str] = loop.create_future()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setblocking(False)

    transport, _ = await loop.create_datagram_endpoint(
        lambda: _SSDPProtocol(future),
        sock=sock,
    )

    try:
        transport.sendto(SSDP_REQUEST.encode(), (SSDP_MULTICAST_ADDR, SSDP_PORT))
        logger.info("Sent SSDP M-SEARCH for Denon AVR")

        try:
            ip = await asyncio.wait_for(future, timeout=SSDP_TIMEOUT)
            logger.info("Discovered AVR at %s", ip)
            return ip
        except asyncio.TimeoutError:
            logger.warning("SSDP discovery timed out — no AVR found")
            return None
    finally:
        transport.close()
