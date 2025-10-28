# src/music_manager/api/routers/spotify.py

from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel

from music_manager.core.database_manager import DatabaseManager
from music_manager.wrappers.spotify_wrapper import SpotifyWrapper
from music_manager.wrappers.plex_wrapper import PlexWrapper
from music_manager.services.playlist_generator import PlaylistGenerator
from music_manager.api.dependencies import get_db, get_spotify, get_plex, get_playlist_generator

router = APIRouter(
    prefix="/spotify",
    tags=["Spotify"],
)

class ManualAdd(BaseModel):
    spotify_uri: str
    artist_name: str
    track_name: str
    album_name: str

@router.post("/track/queue", summary="Manually queue a track for download")
def manual_add_api(track: ManualAdd, db: DatabaseManager = Depends(get_db)):
    """
    Adds a single track to the download queue.
    """
    success, message = db.queue_track(
        spotify_uri=track.spotify_uri,
        artist_name=track.artist_name,
        track_name=track.track_name,
        album_name=track.album_name,
    )
    if not success:
        raise HTTPException(status_code=409, detail=message)
    return {"message": message}

@router.post("/playlist/generate-m3u", summary="Generate an M3U file from a Spotify playlist")
def generate_m3u_api(
    playlist_id: str = Body(..., embed=True),
    spotify: SpotifyWrapper = Depends(get_spotify),
    playlist_gen: PlaylistGenerator = Depends(get_playlist_generator)
):
    """
    Fetches tracks from a Spotify playlist and generates a local .m3u file.
    """
    playlist_name, spotify_uris = spotify.get_playlist_tracks(playlist_id)
    if not playlist_name:
        raise HTTPException(status_code=404, detail=f"Spotify playlist with ID '{playlist_id}' not found or is empty.")
    
    playlist_gen.generate_playlist_from_uris(playlist_name, spotify_uris)
    return {"message": f"M3U playlist generation for '{playlist_name}' initiated."}