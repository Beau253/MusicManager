# src/music_manager/services/playlist_generator.py

import logging
import os
from pathlib import Path
import re

# Import core components
from music_manager.core.config_manager import ConfigManager
from music_manager.core.database_manager import DatabaseManager

# Get the logger for this module
logger = logging.getLogger(__name__)

class PlaylistGenerator:
    """
    Generates playlist files (e.g., .m3u) from a list of Spotify tracks.

    It queries the local database to find the corresponding file paths for each
    track and calculates relative paths for maximum portability.
    """

    def __init__(self, config: ConfigManager, db: DatabaseManager):
        """
        Initializes the PlaylistGenerator.

        Args:
            config: An instance of the ConfigManager.
            db: An instance of the DatabaseManager.
        """
        self.config = config
        self.db = db
        # Get the directory where playlist files will be saved.
        # This is a new path that should be added to the config.
        self.playlist_dir = self.config.get_path("playlist_subdir") # e.g., /music/Playlists

    def _sanitize_filename(self, name: str) -> str:
        """
        Removes characters from a string that are illegal in filenames.
        Also replaces spaces with underscores for cleaner filenames.
        """
        # Remove illegal characters
        sanitized = re.sub(r'[\\/*?:"<>|]', "", name)
        # Optional: Replace spaces with underscores
        # sanitized = sanitized.replace(" ", "_")
        return sanitized

    def generate_playlist_from_uris(self, playlist_name: str, spotify_uris: list[str]):
        """
        Generates or updates a single .m3u playlist file.

        This is the main method for this service. It takes a list of Spotify URIs
        in the desired order and constructs the playlist.

        Args:
            playlist_name: The desired name of the playlist (e.g., "My Favorite Hits").
            spotify_uris: A list of Spotify track URIs in the correct playlist order.
        """
        if not self.config.get_feature_setting("m3u_generator_enabled"):
            logger.info("M3U playlist generation is disabled in the configuration. Skipping.")
            return

        logger.info(f"Generating .m3u playlist for: '{playlist_name}'")

        sanitized_name = self._sanitize_filename(playlist_name)
        m3u_path = self.playlist_dir / f"{sanitized_name}.m3u"
        
        # Ensure the output directory exists
        self.playlist_dir.mkdir(parents=True, exist_ok=True)
        
        # Fetch all file paths from the database in one go for efficiency
        # This returns a dictionary mapping {spotify_uri: relative_path}
        path_map = self.db.get_paths_for_uris(spotify_uris)

        successful_tracks = 0
        total_tracks = len(spotify_uris)

        try:
            with open(m3u_path, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                
                for uri in spotify_uris:
                    relative_path_str = path_map.get(uri)
                    
                    if relative_path_str:
                        # The path in the DB is relative to the music_root_dir.
                        # We need to make it relative to the location of the M3U file.
                        
                        # Get absolute paths to calculate the final relative path
                        music_root = self.config.get_path("music_root_dir")
                        absolute_song_path = music_root / relative_path_str
                        
                        try:
                            # Calculate path of the song relative to the M3U file's directory
                            final_relative_path = os.path.relpath(absolute_song_path, self.playlist_dir)
                            
                            # Ensure forward slashes for cross-platform compatibility
                            path_in_m3u = str(Path(final_relative_path)).replace(os.sep, '/')
                            
                            f.write(f"{path_in_m3u}\n")
                            successful_tracks += 1
                            logger.debug(f"Added '{path_in_m3u}' to '{m3u_path.name}'")

                        except ValueError as e:
                            # This can happen on Windows if song and playlist paths are on different drives.
                            logger.error(f"Could not create relative path for track URI '{uri}'. Skipping. Error: {e}")
                    else:
                        logger.warning(f"Could not find a local file for track URI '{uri}' in the database. It may not be organized yet. Skipping.")
            
            logger.info(f"Finished playlist generation for '{playlist_name}'. Successfully added {successful_tracks}/{total_tracks} tracks to {m3u_path}.")

        except IOError as e:
            logger.critical(f"Failed to write to playlist file at '{m3u_path}'. Error: {e}", exc_info=True)