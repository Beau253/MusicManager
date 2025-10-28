# src/music_manager/api/routers/lidarr.py

from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Any

from music_manager.wrappers.lidarr_wrapper import LidarrWrapper
from music_manager.api.dependencies import get_lidarr

router = APIRouter(
    prefix="/lidarr",
    tags=["Lidarr"],
)

@router.get("/queue", summary="Get the Lidarr activity queue")
def get_lidarr_queue(lidarr: LidarrWrapper = Depends(get_lidarr)) -> List[Any]:
    """
    Retrieves the current activity (downloads and imports) from the Lidarr queue.
    """
    if not lidarr.is_configured():
        raise HTTPException(status_code=404, detail="Lidarr is not configured.")
    return lidarr.get_queue()

@router.get("/search/artist", summary="Search for an artist in Lidarr")
def search_artist_api(term: str, lidarr: LidarrWrapper = Depends(get_lidarr)) -> List[Any]:
    """
    Searches for artists by name.
    """
    if not lidarr.is_configured():
        raise HTTPException(status_code=404, detail="Lidarr is not configured.")
    return lidarr.search_artist(term)

@router.post("/artist/add", summary="Add and monitor a new artist")
def add_artist_api(
    artist_id: int = Body(..., embed=True, description="The MusicBrainz Artist ID."),
    lidarr: LidarrWrapper = Depends(get_lidarr)
):
    """
    Adds a new artist to Lidarr by their MusicBrainz Artist ID and sets them
    to be monitored.
    """
    if not lidarr.is_configured():
        raise HTTPException(status_code=404, detail="Lidarr is not configured.")
    
    result = lidarr.add_artist(artist_id)
    return {"message": "Artist added successfully.", "details": result}