# src/music_manager/services/organizer.py

import logging
from pathlib import Path
import mutagen

# Import core components and utilities
from music_manager.core.config_manager import ConfigManager
from music_manager.core.database_manager import DatabaseManager
from music_manager.utils.processes import run_external_process # The same utility used by the downloader

# Get the logger for this module
logger = logging.getLogger(__name__)

class OrganizerService:
    """
    Orchestrates the metadata enrichment and file organization workflow.

    This service finds newly downloaded tracks, processes them with MusicBrainz
    Picard for authoritative metadata tagging and renaming, and then updates

    the application's database with this rich, final metadata.
    """

    def __init__(self, config: ConfigManager, db: DatabaseManager):
        """
        Initializes the OrganizerService.

        Args:
            config: An instance of the ConfigManager.
            db: An instance of the DatabaseManager.
        """
        self.config = config
        self.db = db
        # The path to the pre-configured picard.ini file
        self.picard_config_path = self.config.get_path("picard_config_file")
        # The final destination for organized music
        self.organized_music_path = self.config.get_path("organized_subdir")

    def process_newly_downloaded(self):
        """
        Finds all tracks with status 'download_complete' and processes them.
        """
        logger.info("Starting metadata processing for newly downloaded files...")

        # 1. Fetch all tracks that are ready for processing
        tracks_to_process = self.db.get_tracks_by_status('download_complete')
        if not tracks_to_process:
            logger.info("No newly downloaded files to process.")
            return
            
        logger.info(f"Found {len(tracks_to_process)} file(s) to organize.")

        # 2. Process each track individually for clear logging and error handling
        for track in tracks_to_process:
            spotify_uri = track.get('spotify_uri')
            temp_path = Path(track.get('temp_download_path'))
            
            if not temp_path.exists():
                error_message = f"File not found at '{temp_path}'. Cannot organize."
                logger.error(error_message)
                self.db.update_track_status(spotify_uri, 'picard_failed', error_message)
                continue

            try:
                # Update status to 'processing_picard' to lock the record
                self.db.update_track_status(spotify_uri, 'processing_picard', "Processing with MusicBrainz Picard.")

                # --- Call External Organizer (Picard) ---
                logger.info(f"Organizing file: {temp_path.name}")
                
                # Construct the Picard CLI command.
                # Picard will use the rules in the .ini file to automatically
                # tag, rename, and move the file to the organized directory.
                command = [
                    "picard", # This should be in the system's PATH
                    "--config", str(self.picard_config_path),
                    "--output", str(self.organized_music_path),
                    str(temp_path)
                ]
                
                return_code = run_external_process(command)
                
                # --- Update Database Based on Result ---
                if return_code == 0:
                    # 3. Find the new file path. This is a bit tricky as Picard renames it.
                    # We will need a robust method to find the final path.
                    # For now, let's assume a function `find_organized_file` exists.
                    final_path = self._find_organized_file(spotify_uri) # Placeholder
                    
                    if not final_path:
                         raise FileNotFoundError("Could not locate the final organized file after Picard ran.")

                    logger.info(f"Picard processing successful. New file at: {final_path}")
                    
                    # 4. Read the final, authoritative metadata from the new file
                    metadata = self._read_final_metadata(final_path)
                    
                    # 5. Populate the 'metadata' table in the database
                    self.db.add_or_update_metadata(track.get('id'), metadata)
                    
                    # 6. Update the 'tracks' table to its final state
                    relative_final_path = self.config.get_relative_path(final_path) # New ConfigManager helper
                    self.db.update_track_status(spotify_uri, 'organized', "Successfully organized and tagged.")
                    self.db.update_final_path(spotify_uri, str(relative_final_path))
                    
                else:
                    error_message = f"Picard failed with exit code {return_code}."
                    self.db.update_track_status(spotify_uri, 'picard_failed', error_message)
                    logger.error(error_message)

            except Exception as e:
                error_message = f"An unexpected error occurred while organizing track {spotify_uri}: {e}"
                logger.critical(error_message, exc_info=True)
                self.db.update_track_status(spotify_uri, 'picard_failed', error_message)
                continue
                
        logger.info("Metadata processing finished.")

    def _find_organized_file(self, spotify_uri: str) -> Path | None:
        """
        Finds the newly organized file. This is a complex task.
        A potential strategy is to search the organized directory for a file
        with a matching MusicBrainz Recording ID in its tags.
        """
        # This is a placeholder for a more complex implementation.
        # For now, we'll simulate finding it.
        logger.debug(f"Searching for final file path for track {spotify_uri}...")
        
        # A real implementation would:
        # 1. Get the MBID from the DB (it would need to be added in an earlier step).
        # 2. Recursively search self.organized_music_path for audio files.
        # 3. For each file, use mutagen to read its MBID tag.
        # 4. Return the path of the file with the matching MBID.
        
        # Simulating finding a path for blueprint purposes:
        track_info = self.db.get_track_details(spotify_uri)
        artist = track_info.get('artist_name_spotify', 'Unknown Artist')
        title = track_info.get('track_name_spotify', 'Unknown Title')
        return self.organized_music_path / artist / f"{title}.m4a"

    def _read_final_metadata(self, file_path: Path) -> dict:
        """
        Reads rich metadata from a tagged audio file using mutagen.
        
        Args:
            file_path: The path to the audio file.
            
        Returns:
            A dictionary of cleaned, authoritative metadata.
        """

        logger.debug(f"Reading final metadata from: {file_path}")
        audio = mutagen.File(file_path)
        if not audio:
            raise IOError("Could not read audio file with mutagen to extract metadata.")
            
        # This function would extract all the relevant fields we defined in the
        # metadata table schema (artist, album, year, MBIDs, etc.) from the
        # mutagen object and return them in a clean dictionary.
        
        # Placeholder for the detailed extraction logic:
        metadata = {
            "musicbrainz_recording_id": audio.get("musicbrainz_recordingid", [None])[0],
            "musicbrainz_release_id": audio.get("musicbrainz_albumid", [None])[0],
            "title": audio.get("title", [None])[0],
            "artist": audio.get("artist", [None])[0],
            "album_artist": audio.get("albumartist", [None])[0],
            "album": audio.get("album", [None])[0],
            "year": int(str(audio.get("date", [0])[0])[:4]),
            "track_number": int(str(audio.get("tracknumber", ["0/0"])[0]).split('/')[0]),
            "length_ms": int(audio.info.length * 1000),
            "file_quality": f"{audio.info.codec.upper()} {audio.info.bitrate // 1000}kbps",
            "final_filepath_relative": str(self.config.get_relative_path(file_path)),
        }
        
        return metadata