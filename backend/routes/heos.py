from fastapi import APIRouter, HTTPException, Query

from ..models import BrowseItem, PlayStationRequest, PlayStateRequest, PresetRequest

router = APIRouter(prefix="/api/heos", tags=["heos"])


def _get_manager():
    from ..main import connection_manager
    return connection_manager


def _to_browse_items(payload: list[dict]) -> list[dict]:
    """Convert HEOS browse payload to BrowseItem dicts."""
    items = []
    for entry in payload:
        item = BrowseItem(
            name=entry.get("name", ""),
            image_url=entry.get("image_url"),
            type=entry.get("type"),
            cid=entry.get("cid"),
            mid=entry.get("mid"),
            sid=entry.get("sid"),
            container=entry.get("container", "no") == "yes",
            playable=entry.get("playable", "no") == "yes",
        )
        items.append(item.model_dump())
    return items


@router.get("/now-playing")
async def get_now_playing():
    mgr = _get_manager()
    if not mgr.heos:
        raise HTTPException(503, "HEOS not connected")
    data = await mgr.heos.get_now_playing()
    await mgr.update_now_playing(data)
    return data


@router.post("/play-state")
async def set_play_state(req: PlayStateRequest):
    mgr = _get_manager()
    if not mgr.heos:
        raise HTTPException(503, "HEOS not connected")
    result = await mgr.heos.set_play_state(req.state)
    await mgr.update_state(play_state=result)
    return {"state": result}


@router.get("/browse/tunein")
async def browse_tunein_root():
    mgr = _get_manager()
    if not mgr.heos:
        raise HTTPException(503, "HEOS not connected")
    payload = await mgr.heos.browse_tunein()
    return _to_browse_items(payload)


@router.get("/browse/tunein/{cid:path}")
async def browse_tunein(cid: str):
    mgr = _get_manager()
    if not mgr.heos:
        raise HTTPException(503, "HEOS not connected")
    payload = await mgr.heos.browse_tunein(cid)
    return _to_browse_items(payload)


@router.post("/play/station")
async def play_station(req: PlayStationRequest):
    mgr = _get_manager()
    if not mgr.heos:
        raise HTTPException(503, "HEOS not connected")
    success = await mgr.heos.play_station(req.sid, req.cid, req.mid, req.name)
    if not success:
        raise HTTPException(500, "Failed to play station")
    return {"status": "ok"}


@router.get("/browse/favorites")
async def browse_favorites():
    mgr = _get_manager()
    if not mgr.heos:
        raise HTTPException(503, "HEOS not connected")
    payload = await mgr.heos.browse_favorites()
    return _to_browse_items(payload)


@router.post("/play/preset")
async def play_preset(req: PresetRequest):
    mgr = _get_manager()
    if not mgr.heos:
        raise HTTPException(503, "HEOS not connected")
    success = await mgr.heos.play_preset(req.preset)
    if not success:
        raise HTTPException(500, "Failed to play preset")
    return {"status": "ok"}


@router.get("/search/tunein")
async def search_tunein(q: str = Query(min_length=1)):
    mgr = _get_manager()
    if not mgr.heos:
        raise HTTPException(503, "HEOS not connected")
    payload = await mgr.heos.search_tunein(q)
    return _to_browse_items(payload)
