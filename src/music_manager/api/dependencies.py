# src/music_manager/api/dependencies.py

from music_manager.core.app_factory import create_app_context
from music_manager.core.database_manager import DatabaseManager
from music_manager.services.downloader_service import DownloaderService
from music_manager.services.playlist_generator import PlaylistGenerator
from music_manager.wrappers.lidarr_wrapper import LidarrWrapper
from music_manager.wrappers.plex_wrapper import PlexWrapper
from music_manager.wrappers.spotify_wrapper import SpotifyWrapper

# This dictionary will hold the single, shared instance of all application components.
_app_context = {}

def initialize_dependencies():
    """
    Initializes the application context using the central factory.
    This should be called once at application startup.
    """
    global _app_context
    if not _app_context:
        _app_context = create_app_context()
        _app_context['db'].connect()

def get_db():
    """FastAPI dependency to get the database manager."""
    return _app_context['db']

def get_plex():
    """FastAPI dependency to get the Plex wrapper."""
    return _app_context['plex']

def get_downloader():
    """FastAPI dependency to get the Downloader service."""
    return _app_context['downloader']

def get_lidarr():
    """FastAPI dependency to get the Lidarr wrapper."""
    return _app_context['lidarr']

def get_spotify():
    """FastAPI dependency to get the Spotify wrapper."""
    return _app_context['spotify']

def get_playlist_generator():
    """FastAPI dependency to get the PlaylistGenerator service."""
    return _app_context['playlist_generator']

def get_config():
    """FastAPI dependency to get the ConfigManager."""
    return _app_context['config']

def get_app_context():
    """FastAPI dependency to get the entire application context."""
    return _app_context