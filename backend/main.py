import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

from .connection_manager import ConnectionManager
from .routes import avr, heos, system

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

connection_manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting denon-vibe backend...")
    await connection_manager.startup()
    yield
    logger.info("Shutting down denon-vibe backend...")
    await connection_manager.shutdown()


app = FastAPI(title="denon-vibe", lifespan=lifespan)

# Include routers
app.include_router(avr.router)
app.include_router(heos.router)
app.include_router(system.router)


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await connection_manager.ws_manager.connect(ws)
    # Send full state on connect
    state = await connection_manager.get_full_state()
    await connection_manager.ws_manager.send_to(ws, {"type": "state", "data": state})
    try:
        # Keep connection alive — we only push, but must read to detect disconnect
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        connection_manager.ws_manager.disconnect(ws)


# Mount frontend static files (production build)
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.is_dir():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="static")


def run():
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
