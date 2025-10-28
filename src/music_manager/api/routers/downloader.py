# src/music_manager/api/routers/downloader.py

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Optional

from music_manager.services.downloader_service import DownloaderService
from music_manager.api.dependencies import get_downloader

router = APIRouter(
    prefix="/downloader",
    tags=["Downloader"],
)

@router.post("/run", summary="Run the downloader process")
def run_downloader_api(
    background_tasks: BackgroundTasks,
    downloader: DownloaderService = Depends(get_downloader)
):
    """
    Triggers the downloader service to process all tracks in the 'queued' state.
    The process is run in the background and the API returns immediately.
    """
    try:
        # Add the long-running task to be executed after the response is sent.
        background_tasks.add_task(downloader.run)
        return {"message": "Downloader process started in the background."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start downloader process: {e}")

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