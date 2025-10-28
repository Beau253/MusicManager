# src/music_manager/core/app_factory.py

import logging
from typing import Dict, Any

from music_manager.core.config_manager import ConfigManager
from music_manager.core.database_manager import DatabaseManager
from music_manager.core.logger import setup_logging
from music_manager.services.downloader_service import DownloaderService
from music_manager.services.playlist_generator import PlaylistGenerator
from music_manager.wrappers.lidarr_wrapper import LidarrWrapper
from music_manager.wrappers.plex_wrapper import PlexWrapper
from music_manager.wrappers.spotify_wrapper import SpotifyWrapper

def create_app_context() -> Dict[str, Any]:
    """
    Initializes and returns all core application components in a dictionary.

    This function acts as a centralized factory for the application's context,
    ensuring that both the CLI and the API use the same instances of core services.

    Returns:
        A dictionary containing all initialized components.
    """
    context = {}
    try:
        # --- 1. Initialize Configuration Manager ---
        config = ConfigManager()
        context['config'] = config

        # --- 2. Initialize Logging ---
        logger = setup_logging(
            log_level_console=config.get_logging_setting("log_level_console"),
            log_level_file=config.get_logging_setting("log_level_file")
        )
        context['logger'] = logger

        # --- 3. Initialize Database Manager ---
        db = DatabaseManager(db_path=config.get_path("database_file"))
        context['db'] = db

        # --- 4. Initialize Wrappers and Services ---
        context['spotify'] = SpotifyWrapper(config)
        context['plex'] = PlexWrapper(config)
        context['lidarr'] = LidarrWrapper(config)
        context['downloader'] = DownloaderService(config=config, db=db)
        context['playlist_generator'] = PlaylistGenerator(config=config, db=db)

        return context
    except Exception as e:
        logging.getLogger(__name__).critical(f"A critical error occurred during application initialization: {e}", exc_info=True)
        exit(1)