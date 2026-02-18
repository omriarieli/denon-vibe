from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["system"])


def _get_manager():
    from ..main import connection_manager
    return connection_manager


@router.get("/status")
async def get_status():
    mgr = _get_manager()
    return await mgr.get_full_state()


@router.post("/discover")
async def discover():
    mgr = _get_manager()
    ip = await mgr.rediscover()
    return {"avr_ip": ip, "connected": mgr.state.connected}
