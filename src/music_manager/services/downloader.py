# src/music_manager/services/downloader.py

import logging
import time
import random
from datetime import datetime

# Import core components and wrappers
from music_manager.core.config_manager import ConfigManager
from music_manager.core.database_manager import DatabaseManager
from music_manager.wrappers.lidarr_wrapper import LidarrWrapper
from music_manager.utils.processes import run_external_process # Assuming a new utility module for this

# Get the logger for this module
logger = logging.getLogger(__name__)

class DownloaderService:
    """
    Orchestrates the track acquisition workflow.

    This service is responsible for fetching queued tracks, checking against Lidarr,
    calling the external downloader ('onthespot'), and updating the database
    with the results of the download attempt.
    """

    def __init__(self, config: ConfigManager, db: DatabaseManager, lidarr: LidarrWrapper):
        """
        Initializes the DownloaderService.

        Args:
            config: An instance of the ConfigManager.
            db: An instance of the DatabaseManager.
            lidarr: An instance of the LidarrWrapper.
        """
        self.config = config
        self.db = db
        self.lidarr = lidarr
        
        # Load downloader settings
        self.daily_limit = self.config.get_downloader_setting("daily_track_limit")
        self.download_format = self.config.get_downloader_setting("download_format")
        # Conceptual: self.onthespot_path = self.config.get_downloader_setting("onthespot_path")
        
        # Placeholder for quota tracking
        # In a real implementation, this would be a separate class that reads/writes the quota file.
        self.quota_usage = self._load_quota_usage()

    def _load_quota_usage(self) -> int:
        """Loads the current daily quota usage from the database or a file."""
        # For now, this is a placeholder. It would query the DB for tracks
        # downloaded today or read from the onthespot_quota.json file.
        logger.debug("Loading daily quota usage...")
        # In a real implementation: return self.db.get_downloads_since(some_timestamp)
        return 10 # Dummy data

    def _save_quota_usage(self):
        """Saves the updated quota usage."""
        logger.debug(f"Saving new quota usage: {self.quota_usage}")
        # In a real implementation, this would write to the onthespot_quota.json file.
        pass

    def process_download_queue(self, limit: int = 0):
        """
        The main method to process the download queue.

        Args:
            limit: An optional limit on the number of tracks to process in this run.
                   If 0, it will process up to the daily quota.
        """
        logger.info("Starting download queue processing...")

        # 1. Check remaining quota
        remaining_quota = self.daily_limit - self.quota_usage
        if remaining_quota <= 0:
            logger.info("Daily download quota reached. No tracks will be processed.")
            return

        # 2. Determine how many tracks to process
        process_limit = remaining_quota if limit == 0 else min(limit, remaining_quota)
        logger.info(f"Daily quota allows for {remaining_quota} more tracks. Processing up to {process_limit}.")

        # 3. Fetch queued tracks from the database
        queued_tracks = self.db.get_tracks_by_status('queued', limit=process_limit)
        if not queued_tracks:
            logger.info("Download queue is empty. Nothing to process.")
            return

        logger.info(f"Found {len(queued_tracks)} tracks in the queue to process.")
        
        # 4. Process each track
        for track in queued_tracks:
            spotify_uri = track.get('spotify_uri')
            
            try:
                # Update status to 'processing_download' to prevent another worker from picking it up
                self.db.update_track_status(spotify_uri, 'processing_download', "Starting download process.")

                # --- Pre-Acquisition Check ---
                if self.lidarr.is_configured():
                    logger.info(f"Checking Lidarr for album: '{track.get('album_name_spotify')}'")
                    album_status = self.lidarr.get_album_status_by_name(
                        artist_name=track.get('artist_name_spotify'),
                        album_name=track.get('album_name_spotify')
                    )
                    
                    if album_status == 'on_disk':
                        logger.info("Album is already 'on_disk' in Lidarr. Skipping download.")
                        self.db.update_track_status(spotify_uri, 'skipped', "Fulfilled by Lidarr (on disk).")
                        self.db.update_lidarr_status(spotify_uri, 'on_disk')
                        continue # Move to the next track
                    elif album_status == 'monitored':
                        self.db.update_lidarr_status(spotify_uri, 'monitored')

                # --- Call External Downloader ('onthespot') ---
                logger.info(f"Downloading: {track.get('artist_name_spotify')} - {track.get('track_name_spotify')}")
                
                # Construct command for the external downloader
                download_path = self.config.get_path('unorganized_subdir')
                command = [
                    "onthespot", # This should be a configurable path
                    "--output", str(download_path),
                    "--format", self.download_format,
                    track.get('spotify_uri')
                ]
                
                # run_external_process is the utility that captures stdout/stderr
                return_code = run_external_process(command)
                
                # --- Update Database Based on Result ---
                if return_code == 0:
                    # In a real implementation, we would need to find the actual file path
                    # that 'onthespot' created to store it in the database.
                    # This is a placeholder.
                    temp_path = download_path / f"{track.get('track_name_spotify')}.{self.download_format}"
                    
                    self.db.update_track_status(spotify_uri, 'download_complete', f"Successfully downloaded to {temp_path}")
                    self.db.update_temp_path(spotify_uri, str(temp_path)) # A new DB method
                    
                    # Update quota
                    self.quota_usage += 1
                    self._save_quota_usage()
                    logger.info("Download successful.")
                else:
                    error_message = f"Downloader failed with exit code {return_code}."
                    self.db.update_track_status(spotify_uri, 'download_failed', error_message)
                    logger.error(error_message)

                # --- Add a polite delay ---
                delay = random.uniform(3, 7)
                logger.debug(f"Waiting for {delay:.1f} seconds before next download...")
                time.sleep(delay)

            except Exception as e:
                error_message = f"An unexpected error occurred while processing track {spotify_uri}: {e}"
                logger.critical(error_message, exc_info=True)
                self.db.update_track_status(spotify_uri, 'download_failed', error_message)
                continue # Continue to the next track even if one fails catastrophically
        
        logger.info("Download queue processing finished.")