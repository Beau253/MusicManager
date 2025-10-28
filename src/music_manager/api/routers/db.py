# src/music_manager/api/routers/db.py

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from music_manager.core.database_manager import DatabaseManager
from music_manager.api.dependencies import get_db
from music_manager.api.models import TrackBase, TrackDetails

router = APIRouter(
    prefix="/db",
    tags=["Database"],
)

@router.get("/tracks", summary="Search for tracks in the database", response_model=List[TrackBase])
def search_tracks_api(
    query: Optional[str] = None,
    status: Optional[str] = None,
    db: DatabaseManager = Depends(get_db),
):
    """
    Searches the database for tracks matching the given criteria.
    This mirrors the `db list` and `downloader view-queue`/`view-failed` commands.
    """
    try:
        tracks = db.search_tracks(query=query, status=status)
        return tracks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")

@router.get("/track/{spotify_uri}", summary="Get details for a specific track", response_model=TrackDetails)
def get_track_details_api(spotify_uri: str, db: DatabaseManager = Depends(get_db)):
    """
    Retrieves detailed information for a single track by its Spotify URI.
    """
    details = db.get_track_details(spotify_uri)
    if not details:
         raise HTTPException(status_code=404, detail=f"Track with URI '{spotify_uri}' not found.")
    return details

@router.delete("/track/{spotify_uri}", summary="Remove a track from the database")
def remove_track_api(spotify_uri: str, db: DatabaseManager = Depends(get_db)):
    """Removes a track and its associated data from the database."""
    success = db.remove_track(spotify_uri)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to remove track.")
    return {"message": f"Track '{spotify_uri}' removed successfully."}