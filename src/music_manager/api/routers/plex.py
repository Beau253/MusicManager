# src/music_manager/api/routers/plex.py

from fastapi import APIRouter, Depends, HTTPException

from music_manager.wrappers.plex_wrapper import PlexWrapper
from music_manager.api.dependencies import get_plex

router = APIRouter(
    prefix="/plex",
    tags=["Plex"],
)

@router.post("/scan-library", summary="Trigger a Plex library scan")
def scan_library_api(plex: PlexWrapper = Depends(get_plex)):
    """
    Initiates a scan of the music library in Plex.
    """
    try:
        plex.scan_library()
        return {"message": "Plex library scan initiated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start Plex scan: {e}")