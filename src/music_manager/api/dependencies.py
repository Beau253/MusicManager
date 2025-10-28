# src/music_manager/api/dependencies.py

import logging
from pathlib import Path

from music_manager.core.config_manager import ConfigManager
from music_manager.core.database_manager import DatabaseManager
from music_manager.services.downloader_service import DownloaderService
from music_manager.wrappers.plex_wrapper import PlexWrapper

# This is a simplified way to manage global state for the API.
# In a larger application, you might use a more robust dependency injection framework
# or FastAPI's `app.state`.

config_manager: ConfigManager = None
db_manager: DatabaseManager = None
logger: logging.Logger = None
plex_wrapper: PlexWrapper = None
downloader_service: DownloaderService = None

def initialize_dependencies():
    """
    Initializes the shared components (config, db, logger) that the API endpoints will need.
    This should be called once at application startup.
    """
    global config_manager, db_manager, logger, plex_wrapper, downloader_service

    # Set up logger
    # In a real scenario, this would be configured more robustly, but for now,
    # we'll use a basic configuration.
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("api")

    # Initialize ConfigManager
    config_path = Path("/config/config.toml") # Using the default path
    config_manager = ConfigManager(config_path=config_path)

    # Initialize DatabaseManager
    db_path = config_manager.get_path("database_file")
    db_manager = DatabaseManager(db_path=db_path)
    db_manager.connect()

    # Initialize Wrappers and Services
    plex_wrapper = PlexWrapper(config_manager)
    downloader_service = DownloaderService(config=config_manager, db=db_manager)

def get_db():
    """FastAPI dependency to get the database manager."""
    return db_manager

def get_plex():
    """FastAPI dependency to get the Plex wrapper."""
    return plex_wrapper

def get_downloader():
    """FastAPI dependency to get the Downloader service."""
    return downloader_service