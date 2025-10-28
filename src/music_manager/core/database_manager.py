# src/music_manager/core/database_manager.py

import logging
import sqlite3
from pathlib import Path
from datetime import datetime

# Get the logger for this module
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages all interactions with the application's SQLite database.

    This class handles connection management, schema creation, and schema migrations.
    It provides a high-level API for all database operations, ensuring that
    the rest of the application doesn't need to write raw SQL.
    """
    def __init__(self, db_path: Path):
        """
        Initializes the DatabaseManager.

        Args:
            db_path: The absolute path to the SQLite database file.
        """
        self.db_path = db_path
        self.conn = None
        
        # --- Migration System ---
        # The target schema version for the current codebase.
        # Increment this number whenever you make a change to the schema.
        self._target_schema_version = 1

    def __enter__(self):
        """Allows the class to be used as a context manager (e.g., 'with DatabaseManager(...) as db:')."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Closes the connection when the context is exited."""
        self.close()

    def connect(self):
        """
        Establishes a connection to the SQLite database.
        Initializes the schema and runs migrations if necessary.
        """
        try:
            # Ensure the parent directory for the database file exists.
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Connect to the database. `check_same_thread=False` is important for
            # multi-threaded applications (like our service log capture).
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            
            # Use the 'Row' factory to allow accessing columns by name (like a dictionary).
            self.conn.row_factory = sqlite3.Row
            
            # Run the initialization and migration logic.
            self._initialize_database()
            logger.info(f"Successfully connected to database at {self.db_path}")

        except sqlite3.Error as e:
            logger.critical(f"Database connection failed: {e}", exc_info=True)
            raise  # Re-raise the exception to halt the application if the DB is inaccessible.

    def close(self):
        """Closes the database connection if it is open."""
        if self.conn:
            self.conn.commit() # Ensure any pending transactions are committed
            self.conn.close()
            self.conn = None
            logger.info("Database connection closed.")

    def _execute(self, sql: str, params: tuple = ()):
        """A helper method to execute SQL and handle logging."""
        if not self.conn:
            raise RuntimeError("Database connection is not open.")
        logger.debug(f"Executing SQL: {sql} with params {params}")
        return self.conn.execute(sql, params)

    def _initialize_database(self):
        """
        Ensures the database is set up correctly. This function checks the
        current schema version and applies all necessary migrations in order.
        """
        # PRAGMA user_version is SQLite's built-in way to store a schema version number.
        cursor = self._execute("PRAGMA user_version;")
        current_version = cursor.fetchone()[0]
        logger.info(f"Database schema version: {current_version}. Target version: {self._target_schema_version}.")

        if current_version < self._target_schema_version:
            self.conn.execute("BEGIN TRANSACTION;")
            try:
                # --- Migration Logic ---
                # Apply migrations sequentially.
                if current_version < 1:
                    self._migrate_to_v1()
                
                # Add future migrations here:
                # if current_version < 2:
                #     self._migrate_to_v2()

                self.conn.commit()
                logger.info("Database migration(s) applied successfully.")
            except sqlite3.Error as e:
                self.conn.rollback()
                logger.critical(f"Database migration failed! Rolling back changes. Error: {e}", exc_info=True)
                raise

    # --- MIGRATION METHODS ---

    def _migrate_to_v1(self):
        """
        Migration to Schema Version 1.
        This creates the initial tables.
        """
        logger.info("Applying migration to schema v1: Creating initial tables...")

        # Create the 'tracks' table for workflow status tracking
        self._execute("""
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                spotify_uri TEXT UNIQUE,
                artist_name_spotify TEXT,
                track_name_spotify TEXT,
                album_name_spotify TEXT,
                status TEXT NOT NULL,
                added_date DATETIME NOT NULL,
                last_attempt_date DATETIME,
                fail_count INTEGER DEFAULT 0,
                error_message TEXT,
                temp_download_path TEXT,
                local_path TEXT,
                musicbrainz_recording_id TEXT,
                status_lidarr TEXT DEFAULT 'unknown',
                status_plex TEXT DEFAULT 'unknown'
            );
        """)

        # Create the 'metadata' table for rich, canonical data
        self._execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                track_db_id INTEGER UNIQUE,
                musicbrainz_recording_id TEXT UNIQUE,
                musicbrainz_release_id TEXT,
                title TEXT,
                artist TEXT,
                album_artist TEXT,
                album TEXT,
                genre TEXT,
                year INTEGER,
                release_date DATETIME,
                track_number INTEGER,
                disc_number INTEGER,
                length_ms INTEGER,
                file_quality TEXT,
                final_filepath_relative TEXT,
                FOREIGN KEY (track_db_id) REFERENCES tracks (id) ON DELETE CASCADE
            );
        """)
        
        # Create indexes for faster lookups
        self._execute("CREATE INDEX IF NOT EXISTS idx_tracks_status ON tracks (status);")
        self._execute("CREATE INDEX IF NOT EXISTS idx_metadata_artist ON metadata (artist);")

        # Update the schema version number in the database
        self._execute(f"PRAGMA user_version = 1;")
        
    def _migrate_to_v2(self):
        """
        Example of a future migration.
        This function would be called if the schema version is less than 2.
        """
        logger.info("Applying migration to schema v2: Adding a new column...")
        
        # Use an ALTER TABLE statement to add a new column without deleting data.
        # The try/except block handles cases where the column might already exist.
        try:
            self._execute("ALTER TABLE tracks ADD COLUMN new_feature_flag BOOLEAN DEFAULT 0;")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                logger.warning("Column 'new_feature_flag' already exists. Migration may have been partially applied before.")
            else:
                raise
                
        # Update the schema version number in the database
        self._execute(f"PRAGMA user_version = 2;")


    # --- DATA ACCESS METHODS (API for the rest of the app) ---
    
    # The following are placeholder methods for the functionality defined
    # in the blueprint. You would implement the actual SQL for each one.
    
    def search_tracks(self, query: str = None, status: str = None) -> list:
        logger.debug(f"Searching tracks with query='{query}' and status='{status}'")
        
        sql = "SELECT * FROM tracks"
        conditions = []
        params = []

        if query:
            # Search across multiple relevant fields
            conditions.append("(artist_name_spotify LIKE ? OR track_name_spotify LIKE ? OR album_name_spotify LIKE ?)")
            like_query = f"%{query}%"
            params.extend([like_query, like_query, like_query])
        
        if status:
            conditions.append("status = ?")
            params.append(status)

        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
            
        sql += " ORDER BY added_date DESC"

        cursor = self._execute(sql, tuple(params))
        # Convert rows to dictionaries for easier JSON serialization
        return [dict(row) for row in cursor.fetchall()]

    def get_track_details(self, spotify_uri: str) -> dict:
        logger.debug(f"Getting details for Spotify URI: {spotify_uri}")
        
        # This query joins the 'tracks' and 'metadata' tables to get a complete picture.
        sql = """
            SELECT t.*, m.*
            FROM tracks t
            LEFT JOIN metadata m ON t.id = m.track_db_id
            WHERE t.spotify_uri = ?
        """
        cursor = self._execute(sql, (spotify_uri,))
        row = cursor.fetchone()

        if row:
            # Convert the single row to a dictionary
            return dict(row)
        
        # Return None or an empty dict if not found
        return None

    def remove_track(self, spotify_uri: str) -> bool:
        # Placeholder for the CLI 'db remove' command
        logger.debug(f"Removing track with Spotify URI: {spotify_uri}")
        return True
        
    def reset_all_failed_tracks(self) -> int:
        # Placeholder for the CLI 'db retry --all' command
        logger.debug("Resetting all failed tracks.")
        return 5 # Dummy count
        
    def reset_track_status(self, spotify_uri: str) -> bool:
        # Placeholder for the CLI 'db retry <uri>' command
        logger.debug(f"Resetting status for track: {spotify_uri}")
        return True

    def queue_track(self, spotify_uri, artist_name, track_name, album_name) -> tuple[bool, str]:
        # Placeholder for the CLI 'spotify manual-add' command
        logger.debug(f"Queuing track: {spotify_uri}")
        return True, f"Successfully queued track '{artist_name} - {track_name}'."

    def get_paths_for_uris(self, spotify_uris: list[str]) -> dict:
        """
        Fetches a mapping of Spotify URIs to their final relative file paths for
        a given list of URIs.
        """
        if not spotify_uris:
            return {}
        
        # Use a parameterized query to avoid SQL injection
        placeholders = ','.join('?' for _ in spotify_uris)
        sql = f"SELECT spotify_uri, local_path FROM tracks WHERE spotify_uri IN ({placeholders}) AND status = 'organized'"
        
        cursor = self._execute(sql, tuple(spotify_uris))
        
        # Return a dictionary for fast lookups
        return {row['spotify_uri']: row['local_path'] for row in cursor.fetchall()}