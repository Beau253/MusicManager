# src/music_manager/api/routers/lidarr.py

from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Any

from music_manager.wrappers.lidarr_wrapper import LidarrWrapper
from music_manager.api.dependencies import get_lidarr
from music_manager.api.models import LidarrQueueItem, LidarrArtistSearchResult


router = APIRouter(
    prefix="/lidarr",
    tags=["Lidarr"],
)

@router.get("/queue", summary="Get the Lidarr activity queue", response_model=List[LidarrQueueItem])
def get_lidarr_queue(lidarr: LidarrWrapper = Depends(get_lidarr)):
    """
    Retrieves the current activity (downloads and imports) from the Lidarr queue.
    """
    if not lidarr.is_configured():
        raise HTTPException(status_code=404, detail="Lidarr is not configured.")
    return lidarr.get_queue() # FastAPI will validate this against the response_model


@router.get("/search/artist", summary="Search for an artist in Lidarr", response_model=List[LidarrArtistSearchResult])
def search_artist_api(term: str, lidarr: LidarrWrapper = Depends(get_lidarr)):
    """
    Searches for artists by name.
    """
    if not lidarr.is_configured():
        raise HTTPException(status_code=404, detail="Lidarr is not configured.")
    return lidarr.search_artist(term)

@router.post("/artist/add", summary="Add and monitor a new artist", response_model=LidarrArtistSearchResult)
def add_artist_api(
    musicbrainz_id: str = Body(..., embed=True, description="The MusicBrainz Artist ID (foreignArtistId)."),
    lidarr: LidarrWrapper = Depends(get_lidarr)
):
    """
    Adds a new artist to Lidarr using their MusicBrainz Artist ID and sets them
    to be monitored. The MusicBrainz ID can be found by using the
    `/lidarr/search/artist` endpoint first.
    """
    if not lidarr.is_configured():
        raise HTTPException(status_code=404, detail="Lidarr is not configured.")
    
    # The add_artist method in the wrapper should return the newly created artist object from Lidarr's API
    new_artist = lidarr.add_artist(musicbrainz_id)
    if not new_artist or "id" not in new_artist:
        raise HTTPException(status_code=500, detail="Failed to add artist in Lidarr or parse the response.")
    return new_artist