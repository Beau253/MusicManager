# src/music_manager/api/routers/downloader.py

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from music_manager.services.downloader_service import DownloaderService
from music_manager.api.dependencies import get_downloader

router = APIRouter(
    prefix="/downloader",
    tags=["Downloader"],
)

@router.post("/run", summary="Run the downloader process")
def run_downloader_api(downloader: DownloaderService = Depends(get_downloader)):
    """
    Triggers the downloader service to process all tracks in the 'queued' state.
    This is an asynchronous operation on the backend.
    """
    try:
        # In a real-world scenario, this would likely be a background task.
        # For simplicity, we run it directly but should not block for long.
        downloader.run()
        return {"message": "Downloader process initiated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run downloader: {e}")

@router.post("/retry", summary="Retry failed downloads")
def retry_failed_api(
    spotify_uri: Optional[str] = None,
    downloader: DownloaderService = Depends(get_downloader)
):
    """
    Retries failed downloads. If a Spotify URI is provided, retries a specific track.
    Otherwise, retries all tracks currently in a 'failed' state.
    """
    count = downloader.retry_failed_downloads(spotify_uri=spotify_uri)
    if spotify_uri:
        return {"message": f"Track '{spotify_uri}' has been re-queued for download."}
    return {"message": f"Successfully re-queued {count} failed tracks for download."}