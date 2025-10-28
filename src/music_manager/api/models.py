# src/music_manager/api/models.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class TrackBase(BaseModel):
    """
    Pydantic model representing the core information for a track in the database.
    This provides type validation and serialization for API responses.
    """
    id: int
    spotify_uri: str
    artist_name_spotify: Optional[str] = None
    track_name_spotify: Optional[str] = None
    album_name_spotify: Optional[str] = None
    status: str
    added_date: datetime
    last_attempt_date: Optional[datetime] = None
    fail_count: int = 0
    error_message: Optional[str] = None
    local_path: Optional[str] = None
    musicbrainz_recording_id: Optional[str] = None
    status_lidarr: str = Field(default='unknown')
    status_plex: str = Field(default='unknown')

    class Config:
        orm_mode = True # Allows the model to be created from ORM objects (like sqlite3.Row)

class TrackDetails(TrackBase):
    """
    A more detailed model for a single track, including its metadata.
    """
    # Fields from the 'metadata' table
    title: Optional[str] = None
    artist: Optional[str] = None
    album_artist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    release_date: Optional[datetime] = None
    track_number: Optional[int] = None
    disc_number: Optional[int] = None
    length_ms: Optional[int] = None
    file_quality: Optional[str] = None
    final_filepath_relative: Optional[str] = None