from fastapi import APIRouter, HTTPException

from ..config import INPUT_SOURCES
from ..models import SleepRequest, SourceRequest, VolumeRequest

router = APIRouter(prefix="/api/avr", tags=["avr"])


def _get_manager():
    from ..main import connection_manager
    return connection_manager


@router.get("/power")
async def get_power():
    mgr = _get_manager()
    if not mgr.avr:
        raise HTTPException(503, "AVR not connected")
    power = await mgr.avr.get_power()
    await mgr.update_state(power=power)
    return {"power": power}


@router.post("/power/on")
async def power_on():
    mgr = _get_manager()
    if not mgr.avr:
        raise HTTPException(503, "AVR not connected")
    result = await mgr.avr.power_on()
    await mgr.update_state(power=result)
    return {"power": result}


@router.post("/power/off")
async def power_off():
    mgr = _get_manager()
    if not mgr.avr:
        raise HTTPException(503, "AVR not connected")
    result = await mgr.avr.power_off()
    await mgr.update_state(power=result)
    return {"power": result}


@router.get("/volume")
async def get_volume():
    mgr = _get_manager()
    if not mgr.avr:
        raise HTTPException(503, "AVR not connected")
    volume = await mgr.avr.get_volume()
    await mgr.update_state(volume=volume)
    return {"volume": volume}


@router.post("/volume")
async def set_volume(req: VolumeRequest):
    mgr = _get_manager()
    if not mgr.avr:
        raise HTTPException(503, "AVR not connected")
    level = await mgr.avr.set_volume(req.level)
    await mgr.update_state(volume=level)
    return {"volume": level}


@router.post("/volume/up")
async def volume_up():
    mgr = _get_manager()
    if not mgr.avr:
        raise HTTPException(503, "AVR not connected")
    await mgr.avr.volume_up()
    volume = await mgr.avr.get_volume()
    await mgr.update_state(volume=volume)
    return {"volume": volume}


@router.post("/volume/down")
async def volume_down():
    mgr = _get_manager()
    if not mgr.avr:
        raise HTTPException(503, "AVR not connected")
    await mgr.avr.volume_down()
    volume = await mgr.avr.get_volume()
    await mgr.update_state(volume=volume)
    return {"volume": volume}


@router.post("/mute/toggle")
async def toggle_mute():
    mgr = _get_manager()
    if not mgr.avr:
        raise HTTPException(503, "AVR not connected")
    result = await mgr.avr.toggle_mute()
    await mgr.update_state(mute=result)
    return {"mute": result}


@router.get("/sleep")
async def get_sleep():
    mgr = _get_manager()
    if not mgr.avr:
        raise HTTPException(503, "AVR not connected")
    sleep = await mgr.avr.get_sleep()
    await mgr.update_state(sleep=sleep)
    return {"sleep": sleep}


@router.post("/sleep")
async def set_sleep(req: SleepRequest):
    mgr = _get_manager()
    if not mgr.avr:
        raise HTTPException(503, "AVR not connected")
    result = await mgr.avr.set_sleep(req.minutes)
    await mgr.update_state(sleep=result, force_broadcast=True)
    return {"sleep": result}


@router.get("/source")
async def get_source():
    mgr = _get_manager()
    if not mgr.avr:
        raise HTTPException(503, "AVR not connected")
    source = await mgr.avr.get_source()
    await mgr.update_state(source=source)
    return {"source": source, "sources": INPUT_SOURCES}


@router.post("/source")
async def set_source(req: SourceRequest):
    mgr = _get_manager()
    if not mgr.avr:
        raise HTTPException(503, "AVR not connected")
    if req.source not in INPUT_SOURCES:
        raise HTTPException(400, f"Unknown source: {req.source}")
    result = await mgr.avr.set_source(req.source)
    await mgr.update_state(source=result)
    return {"source": result}
