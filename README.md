# denon-vibe

Web remote control for Denon AVR-1400H. Dark-themed, mobile-first UI that runs in the browser.

Uses **Denon AVR telnet** (port 23) for hardware controls and **HEOS CLI** (port 1255) for streaming/radio. The receiver is auto-discovered on the local network via SSDP.

![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue) ![Svelte 5](https://img.shields.io/badge/svelte-5-orange)

## Features

- **Power** on/off
- **Volume** slider (0-98) + mute toggle
- **Input source** selection (TV Audio, HEOS, Bluetooth, etc.)
- **Sleep timer** presets (15/30/60/90/120 min)
- **Now playing** with album art, play/pause/stop
- **HEOS Favorites** — tap to play
- **TuneIn Radio** browser with search
- **Real-time sync** — changes from the physical remote, other apps, or the UI all stay in sync via WebSocket

## Quick Start

```bash
# Clone and install backend
cd denon-vibe
python -m venv .venv
.venv/bin/pip install fastapi 'uvicorn[standard]'

# Build frontend
cd frontend
npm install
npm run build
cd ..

# Run (serves UI at http://localhost:8000)
.venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Open **http://localhost:8000** on your phone or browser. The AVR is discovered automatically.

## Development

Run backend and frontend dev server separately for hot reload:

```bash
# Terminal 1 — backend
.venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 — frontend (proxies API to backend)
cd frontend
npm run dev
```

Frontend dev server runs at http://localhost:5173.

## Architecture

```
Browser  <──WebSocket──>  FastAPI  <──TCP:23──>   Denon AVR (power, volume, mute, sleep, source)
                             │
                             └─────TCP:1255──>  HEOS CLI (browse, play, favorites, now-playing)
                                   (x2: commands + events)
```

- **REST API** for commands (`/api/avr/*`, `/api/heos/*`, `/api/status`)
- **WebSocket** (`/ws`) for push-only state updates from any source
- **Two HEOS connections**: one for request/response, one for change events (per HEOS spec)
- **State cache** in `ConnectionManager` — avoids polling, updated by command responses + events

## API

### AVR — `/api/avr`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/power` | Get power state |
| POST | `/power/on` | Power on |
| POST | `/power/off` | Standby |
| GET | `/volume` | Get volume |
| POST | `/volume` | Set volume `{"level": 30}` |
| POST | `/volume/up` | Volume up |
| POST | `/volume/down` | Volume down |
| POST | `/mute/toggle` | Toggle mute |
| GET | `/sleep` | Get sleep timer |
| POST | `/sleep` | Set sleep `{"minutes": 30}` (0=off) |
| GET | `/source` | Get current input source |
| POST | `/source` | Set source `{"source": "TV"}` |

### HEOS — `/api/heos`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/now-playing` | Current track/station |
| POST | `/play-state` | `{"state": "play\|pause\|stop"}` |
| GET | `/browse/tunein` | TuneIn top-level |
| GET | `/browse/tunein/{cid}` | Browse TuneIn container |
| GET | `/browse/favorites` | HEOS favorites |
| POST | `/play/station` | Play station `{"sid", "cid", "mid", "name"}` |
| POST | `/play/preset` | Play favorite `{"preset": 1}` |
| GET | `/search/tunein?q=` | Search TuneIn |

### System — `/api`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/status` | Full cached state |
| POST | `/discover` | Re-run SSDP discovery |

## Tech Stack

- **Backend**: Python / FastAPI / uvicorn / asyncio TCP sockets
- **Frontend**: Svelte 5 / Vite
- **Dependencies**: `fastapi` and `uvicorn[standard]` — protocols implemented with stdlib only
