# src/music_manager/services/validation_service.py

import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

class ValidationService:
    """
    A service dedicated to validating all external connections and configurations.
    """
    def __init__(self, app_context: Dict[str, Any]):
        """
        Initializes the service with the application context.

        Args:
            app_context: The dictionary containing all initialized app components.
        """
        self.spotify = app_context.get('spotify')
        self.plex = app_context.get('plex')
        self.lidarr = app_context.get('lidarr')
        self.config = app_context.get('config')

    def run_all_checks(self) -> List[Tuple[str, bool, str]]:
        """
        Runs all validation checks and returns a list of results.

        Returns:
            A list of tuples, where each tuple contains:
            (check_name, success_status, message)
        """
        results = []
        logger.info("Running all validation checks...")

        # --- Spotify Check ---
        if self.spotify and self.spotify.is_configured():
            success, msg = self.spotify.validate_connection()
            results.append(("Spotify Connection", success, msg))
        else:
            results.append(("Spotify Connection", False, "Spotify is not configured in config.toml."))

        # --- Plex Check ---
        if self.plex and self.plex.is_configured():
            success, msg = self.plex.validate_connection()
            results.append(("Plex Connection", success, msg))
        else:
            results.append(("Plex Connection", False, "Plex is not configured in config.toml."))

        # --- Lidarr Check ---
        if self.lidarr and self.lidarr.is_configured():
            success, msg = self.lidarr.validate_connection()
            results.append(("Lidarr Connection", success, msg))
        else:
            results.append(("Lidarr Connection", False, "Lidarr is not configured in config.toml."))

        # --- Path Checks ---
        # You could add checks here to ensure music directories exist and are writable.
        music_root = self.config.get_path("music_root_dir")
        success = music_root.is_dir() and music_root.exists()
        msg = f"Path exists and is a directory." if success else f"Path does not exist or is not a directory."
        results.append((f"Music Root Path ({music_root})", success, msg))

        return results