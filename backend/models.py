from pydantic import BaseModel, Field


class VolumeRequest(BaseModel):
    level: int = Field(ge=0, le=98)


class SleepRequest(BaseModel):
    minutes: int = Field(ge=0, le=120)


class PlayStateRequest(BaseModel):
    state: str = Field(pattern="^(play|pause|stop)$")


class PlayStationRequest(BaseModel):
    sid: int
    cid: str
    mid: str
    name: str


class PresetRequest(BaseModel):
    preset: int = Field(ge=1)


class SourceRequest(BaseModel):
    source: str


class AVRState(BaseModel):
    power: str | None = None
    volume: int | None = None
    mute: str | None = None
    sleep: str | None = None


class NowPlaying(BaseModel):
    type: str | None = None
    song: str | None = None
    album: str | None = None
    artist: str | None = None
    image_url: str | None = None
    station: str | None = None
    mid: str | None = None
    qid: int | None = None
    sid: int | None = None


class BrowseItem(BaseModel):
    name: str
    image_url: str | None = None
    type: str | None = None
    cid: str | None = None
    mid: str | None = None
    sid: int | None = None
    container: bool = False
    playable: bool = False


class AppState(BaseModel):
    connected: bool = False
    avr_ip: str | None = None
    player_id: int | None = None
    power: str | None = None
    volume: int | None = None
    mute: str | None = None
    sleep: str | None = None
    source: str | None = None
    play_state: str | None = None
    now_playing: NowPlaying | None = None
