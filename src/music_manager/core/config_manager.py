# src/music_manager/core/config_manager.py

import logging
import os
from pathlib import Path
import tomli
import tomli_w

# Get the logger for this module
logger = logging.getLogger(__name__)

# Define the default root directory for configuration.
# This fixed path is ideal for containerized environments (e.g., Docker),
# where a host volume can be reliably mapped to `/config`.
DEFAULT_CONFIG_DIR = Path("/config")

class ConfigManager:
    """
    Manages the application's configuration via a TOML file.

    Handles loading, creating, updating, and saving configuration settings,
    ensuring a predictable and persistent state. It prioritizes a fixed path
    for container compatibility.
    """
    def __init__(self, config_path: Path = None):
        """
        Initializes the ConfigManager.

        Args:
            config_path: The path to the config.toml file. If None, defaults
                         to /config/config.toml.
        """
        self.config_path = config_path or DEFAULT_CONFIG_DIR / "config.toml"
        self.config = {}
        self.load_config()

    def _create_default_config(self):
        """
        Creates a default configuration file if one does not exist.
        This ensures the application has a valid starting point on first run.
        """
        logger.warning(f"Configuration file not found. Creating a default one at: {self.config_path}")
        
        default_config = {
            "main": {
                "music_root_dir": "/music",
                "unorganized_subdir": "unorganized_downloads",
                "organized_subdir": "organized_library",
            },
            "spotify": {
                "client_id": "YOUR_SPOTIFY_CLIENT_ID",
                "client_secret": "YOUR_SPOTIFY_CLIENT_SECRET",
                "playlist_urls": [],
            },
            "downloader": {
                "daily_track_limit": 75,
                "download_format": "m4a",
                "download_bitrate": "auto",
            },
            "plex": {
                "url": "http://PLEX_IP_OR_HOSTNAME:32400",
                "token": "YOUR_PLEX_TOKEN",
                "library_name": "Music",
            },
            "lidarr": {
                "url": "http://LIDARR_IP_OR_HOSTNAME:8686",
                "api_key": "YOUR_LIDARR_API_KEY",
            },
            "features": {
                "m3u_generator_enabled": True,
                "plex_playlist_sync_enabled": True,
            },
            "logging": {
                "log_level_console": "INFO",
                "log_level_file": "DEBUG",
            },
            "support": {
                "discord_invite_url": "https://discord.gg/YOUR_INVITE_CODE",
            }
        }
        
        # Ensure the parent directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the default configuration to the file
        self.config = default_config
        self.save_config()

    def load_config(self):
        """
        Loads the configuration from the .toml file. If the file doesn't exist,
        it calls the method to create a default one.
        """
        try:
            with open(self.config_path, "rb") as f:
                self.config = tomli.load(f)
            logger.info(f"Successfully loaded configuration from {self.config_path}")
        except FileNotFoundError:
            self._create_default_config()
        except tomli.TOMLDecodeError as e:
            logger.critical(f"Invalid TOML format in {self.config_path}. Please fix or delete the file to regenerate. Error: {e}")
            exit(1)

    def save_config(self):
        """
        Saves the current in-memory configuration back to the .toml file.
        Used by the 'setup' command after updating settings.
        """
        try:
            with open(self.config_path, "wb") as f:
                tomli_w.dump(self.config, f)
            logger.info(f"Configuration successfully saved to {self.config_path}")
        except IOError as e:
            logger.critical(f"Could not write to configuration file at {self.config_path}: {e}")
            exit(1)

    def get_config_as_dict(self) -> dict:
        """Returns the entire configuration as a dictionary."""
        return self.config

    def get_section(self, section_name: str) -> dict:
        """Retrieves an entire section, returning an empty dict if not found."""
        return self.config.get(section_name, {})

    def _get_setting(self, section: str, key: str, default=None):
        """Helper method to safely get a setting."""
        return self.config.get(section, {}).get(key, default)

    # --- Structured Getters for Each Section ---

    def get_main_setting(self, key: str):
        return self._get_setting("main", key)

    def get_spotify_setting(self, key: str):
        # Prioritize environment variables for secrets
        env_key = f"SPOTIPY_{key.upper()}"
        env_var = os.getenv(env_key)
        return env_var if env_var else self._get_setting("spotify", key, [])

    def get_downloader_setting(self, key: str):
        return self._get_setting("downloader", key)

    def get_plex_setting(self, key: str):
        env_key = f"PLEX_{key.upper()}"
        env_var = os.getenv(env_key)
        return env_var if env_var else self._get_setting("plex", key)

    def get_lidarr_setting(self, key: str):
        env_key = f"LIDARR_{key.upper()}"
        env_var = os.getenv(env_key)
        return env_var if env_var else self._get_setting("lidarr", key)

    def get_feature_setting(self, key: str) -> bool:
        return self._get_setting("features", key, False)

    def get_logging_setting(self, key: str) -> str:
        return self._get_setting("logging", key, "INFO")
        
    def get_path(self, key: str) -> Path:
        """
        Retrieves a path value, resolving it relative to the music_root_dir
        for subdirectories, or returning it directly for the root.
        """
        root_dir_str = self.get_main_setting('music_root_dir')
        if not root_dir_str:
            raise ValueError("`music_root_dir` is not defined in the configuration.")
            
        root_dir = Path(root_dir_str)
        
        if key == 'music_root_dir':
            return root_dir
        elif key in ['unorganized_subdir', 'organized_subdir']:
            subdir = self.get_main_setting(key)
            return root_dir / subdir
        elif key == 'database_file':
            # The database is stored relative to the config directory, not the music directory
            return DEFAULT_CONFIG_DIR / "music_manager.db"
        else:
            raise KeyError(f"Path key '{key}' is not a valid path.")

    def update_setting(self, section: str, key: str, value):
        """
        Updates a setting in the in-memory configuration dictionary.
        This does not save the file; call save_config() for that.
        """
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        logger.debug(f"Updated config setting: [{section}].{key} = {value}")